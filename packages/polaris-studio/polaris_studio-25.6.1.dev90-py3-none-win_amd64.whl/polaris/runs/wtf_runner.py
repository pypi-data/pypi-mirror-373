# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path
from textwrap import dedent

from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.db_utils import attach_to_conn, commit_and_close, run_sql_file
from polaris.utils.database.spatialite_utils import spatialite_available

sql_dir = Path(__file__).resolve().parent / "sql" / "baseline_analysis"


def run_baseline_analysis(iteration: ConvergenceIteration, population_scale_factor: float):
    demand_db = ScenarioCompression.maybe_extract(iteration.files.demand_db)
    supply_db = ScenarioCompression.maybe_extract(iteration.files.supply_db)
    result_db = ScenarioCompression.maybe_extract(iteration.files.result_db)

    output_dir = iteration.output_dir / "baseline_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    def run_analysis_files(dir, db_file, spatial):
        try:
            run_templated_files_from_dir(output_dir, population_scale_factor, dir, db_file, supply_db, spatial)
        except Exception:
            logging.warning(f"Failed while processing sql directory {dir} (spatial={spatial})")

    run_analysis_files(sql_dir, demand_db, False)
    if spatialite_available():
        run_analysis_files(sql_dir / "spatial", demand_db, True)
    run_analysis_files(sql_dir / "on_result", result_db, False)


def run_templated_files_from_dir(output_dir, population_scale_factor, dir, db_file, supply_db=None, spatial=False):
    files = list(dir.glob("*template*.sql"))
    run_templated_files(output_dir, population_scale_factor, files, db_file, supply_db, spatial)


def run_templated_files(output_dir, population_scale_factor, files, db_file, supply_db=None, spatial=False):
    if not files:
        return  # nothing to do, don't even try to open the db
    with commit_and_close(db_file, spatial=spatial) as conn:
        if supply_db is not None:
            attach_to_conn(conn, {"a": supply_db})
        for f in files:
            run_templated_file_on_conn(output_dir, population_scale_factor, f, conn)


def run_templated_file_on_conn(output_dir, population_scale_factor, f, conn):
    rendered_file = output_dir / f.name.replace(".template", "")
    render_wtf_file(f, population_scale_factor, rendered_file)

    logging.debug(f"Running baseline analysis sql file: {rendered_file}")
    sql_timings = run_sql_file(rendered_file, conn)

    timing_file = output_dir / f.name.replace(".template.sql", ".timing.tsv")
    sql_timings.to_csv(timing_file)


def render_wtf_file(input_file, population_scale_factor, output_file=None):
    logging.debug("Rendering {input_file}")
    with open(input_file, "r") as f:
        sql = render_sql(f.read(), population_scale_factor)

    if output_file is not None:
        with open(output_file, "w") as f:
            f.write(sql)
    return sql


def render_sql(sql, population_scale_factor):
    sql = "\n".join(x for x in sql.split("\n") if x[:2] != "--")
    for tag, content in replacements.items():
        sql = sql.replace(tag, content)
    sql = sql.replace("scaling_factor", str(1.0 / population_scale_factor))
    return sql


replacements = {
    "activity_stage_fn": "(CASE WHEN a.trip == 0 THEN 'planned' ELSE 'executed' END)",
    "person_type_fn": dedent(
        """CASE WHEN (p.employment = 4 OR p.employment = 1) AND work_hours >= 30     THEN 'FULLTIME_WORKER'
                WHEN (p.employment = 4 OR p.employment = 1)                          THEN 'PARTTIME_WORKER'
                WHEN (school_enrollment = 3 OR school_enrollment = 2) AND p.age > 18 THEN 'ADULT_STUDENT'
                WHEN p.age >= 65                                                     THEN 'SENIOR'
                WHEN p.age < 65 AND p.age > 18                                       THEN 'NONWORKER'
                WHEN p.age >= 16 AND p.age <= 18                                     THEN 'STUDENT_DRIVER'
                WHEN p.age < 16 AND p.age >= 5                                       THEN 'SCHOOL_CHILD'
                WHEN p.age < 5                                                       THEN 'PRESCHOOL'
                ELSE                                                                      'NONWORKER'
           END"""
    ).strip(),
    "activity_type_fn": dedent(
        """CASE WHEN a.type='EAT OUT'         THEN 'EAT_OUT'
                WHEN a.type='ERRANDS'         THEN 'ERRANDS'
                WHEN a.type='HEALTHCARE'      THEN 'HEALTHCARE'
                WHEN a.type='HOME'            THEN 'HOME'
                WHEN a.type='LEISURE'         THEN 'LEISURE'
                WHEN a.type='PERSONAL'        THEN 'PERSONAL_BUSINESS'
                WHEN a.type='PICKUP-DROPOFF'  THEN 'PICKUP_DROPOFF'
                WHEN a.type='RELIGIOUS-CIVIC' THEN 'RELIGIOUS_OR_CIVIC'
                WHEN a.type='SCHOOL'          THEN 'SCHOOL'
                WHEN a.type='SERVICE'         THEN 'SERVICE_VEHICLE'
                WHEN a.type='SHOP-MAJOR'      THEN 'MAJOR_SHOPPING'
                WHEN a.type='SOCIAL'          THEN 'SOCIAL'
                WHEN a.type='WORK'            THEN 'WORK'
                WHEN a.type='WORK AT HOME'    THEN 'WORK'
                WHEN a.type='PART_WORK'       THEN 'PART_TIME_WORK'
                WHEN a.type='SHOP-OTHER'      THEN 'OTHER_SHOPPING'
                WHEN a.type='EV_CHARGING'     THEN 'EV_CHARGING'
                ELSE                               'MISSING:' || type
                END"""
    ).strip(),
    "transit_mode_fn": dedent(
        """CASE WHEN tr."type" = 0  THEN 'TRAM'
                WHEN tr."type" = 1  THEN 'METRO'
                WHEN tr."type" = 2  THEN 'COMM'
                WHEN tr."type" = 3  THEN 'BUS'
                WHEN tr."type" = 4  THEN 'FERRY'
                WHEN tr."type" = 5  THEN 'CABLE'
                WHEN tr."type" = 6  THEN 'LIFT'
                WHEN tr."type" = 7  THEN 'FUNICULAR'
                WHEN tr."type" = 11 THEN 'TROLLEY'
                WHEN tr."type" = 12 THEN 'MONO'
	       END"""
    ).strip(),
    "mode_fn": dedent(
        """CASE "mode"
           WHEN 0  THEN 'SOV'
           WHEN 2  THEN 'HOV'
           WHEN 4  THEN 'BUS'
           WHEN 5  THEN 'RAIL'
           WHEN 6  THEN 'NONMOTORIZED'
           WHEN 7  THEN 'BICYCLE'
           WHEN 8  THEN 'WALK'
           WHEN 9  THEN 'TAXI'
           WHEN 10 THEN 'SCHOOLBUS'
           WHEN 11 THEN 'PARK_AND_RIDE'
           WHEN 12 THEN 'KISS_AND_RIDE'
           WHEN 13 THEN 'PARK_AND_RAIL'
           WHEN 14 THEN 'KISS_AND_RAIL'
           WHEN 15 THEN 'TNC_AND_RIDE'
           WHEN 16 THEN 'TNC_AND_RAIL'
           WHEN 25 THEN 'RIDE_AND_UNPARK'
           WHEN 26 THEN 'RIDE_AND_REKISS'
           WHEN 27 THEN 'RAIL_AND_UNPARK'
           WHEN 28 THEN 'RAIL_AND_REKISS'
           END"""
    ).strip(),
    "time_of_day_fn": dedent(
        """CASE
           WHEN "start_time" <= 5                         THEN '1.NIGHT'
           WHEN "start_time" >= 6  AND "start_time" <= 8  THEN '2.AMPEAK'
           WHEN "start_time" >= 9  AND "start_time" <= 11 THEN '3.AMOFFPEAK'
           WHEN "start_time" >= 12 AND "start_time" <= 15 THEN '4.PMOFFPEAK'
           WHEN "start_time" >= 16 AND "start_time" <= 18 THEN '5.PMPEAK'
           WHEN "start_time" >= 19 AND "start_time" <= 23 THEN '6.EVENING'
           END"""
    ),
    "income_quintile_fn": dedent(
        """CASE
           WHEN household.income <= 27026                               then 'QUINTILE_1'
           WHEN household.income <= 52179  and household.income > 27026 then 'QUINTILE_2'
           WHEN household.income <= 85076  and household.income > 52179 then 'QUINTILE_3'
           WHEN household.income <= 141110 and household.income > 85076 then 'QUINTILE_4'
           WHEN household.income > 141110                               then 'QUINTILE_5'
    end"""
    ).strip(),
    "race_fn": dedent(
        """CASE WHEN p.race = 1 THEN 'White_alone'
                WHEN p.race = 2 THEN 'Black_alone'
                WHEN p.race = 3 THEN 'American_Indian_alone'
                WHEN p.race = 4 THEN 'Alaskan_Native_alone'
                WHEN p.race = 5 THEN 'American_Indian_other'
                WHEN p.race = 6 THEN 'Asian_alone'
                WHEN p.race = 7 THEN 'Pacific_Islander_alone'
                WHEN p.race = 8 THEN 'Other_race_alone'
                WHEN p.race = 9 THEN 'Two_or_more_races'
           END"""
    ),
    "gender_fn": dedent(
        """
        Case WHEN p.gender = 1 THEN 'Male'
             WHEN p.gender = 2 THEN 'Female'
        END"""
    ),
    "transit_modes": "'BUS', 'RAIL', 'PARK_AND_RAIL', 'PARK_AND_RIDE', 'TNC_AND_RIDE', 'RAIL_AND_UNPARK', 'RIDE_AND_UNPARK'",
}
