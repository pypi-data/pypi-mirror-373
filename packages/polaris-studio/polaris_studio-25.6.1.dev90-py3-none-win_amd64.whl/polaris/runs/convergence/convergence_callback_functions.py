# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path

from sqlalchemy import create_engine, text

from polaris.analyze.kpi_utils import standard_kpis
from polaris.network.utils.rsu_sampler import RsuSampler
from polaris.runs.calibrate.calibration import end_of_loop_fn_for_calibration
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig, KpiFilterConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.gap_reporting import generate_gap_report
from polaris.runs.person_gaps import generate_person_gaps
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.run_utils import copy_replace_file
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.runs.scenario_file import find_next_available_filename, get_scenario_value
from polaris.runs.statistics_db.statistics_db import record_statistics
from polaris.runs.summary import aggregate_summaries
from polaris.runs.wtf_runner import run_baseline_analysis
from polaris.utils.copy_utils import magic_copy
from polaris.utils.database.db_utils import (
    add_column_unless_exists,
    commit_and_close,
    has_table,
    read_and_close,
    run_sql_file,
    table_to_csv,
)
from polaris.utils.db_config import DbConfig
from polaris.utils.func_utils import can_fail
from polaris.utils.logging_utils import function_logging

sql_dir = Path(__file__).resolve().parent.parent / "sql"
if not sql_dir.exists():
    raise RuntimeError("Something went wrong")


def do_nothing(*args, **kwargs):
    pass


def clean_db_for_abm(input_files: PolarisInputs, modelling_freight_deliveries: bool):
    logging.info(f"  Cleaning database for ABM")
    with commit_and_close((input_files.demand_db)) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.execute("delete from activity;")
        conn.execute(
            "update trip set vehicle = NULL, person = NULL, path = -1, path_multimodal = -1, experienced_gap = 1.0;"
        )

        # Delete trips which aren't external (22) or cristal (34)
        trip_types_to_keep = "(22)" if modelling_freight_deliveries else "(22,34)"
        conn.execute(f"delete from trip where type not in {trip_types_to_keep};")
        conn.execute("PRAGMA foreign_keys = ON;")


def clean_db_for_dta(input_files: PolarisInputs):  # pragma : no cover
    logging.info(f"  Cleaning database for DTA ")
    with commit_and_close((input_files.demand_db)) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.execute("delete from trip where mode not in (0, 9, 17, 18, 19, 20);")
        conn.execute("update trip set path = -1 WHERE mode == 9;")
        conn.execute("PRAGMA foreign_keys = ON;")


def copy_log_to(output_dir, destination_dir, name):
    src_file = output_dir / "log" / "polaris_progress.log"
    dest_file = find_next_available_filename(destination_dir / name, separator=".")
    logging.info(f"Copying log file ({src_file}) to ({dest_file})")
    magic_copy(src_file, dest_file, recursive=False)


def default_iterations_fn(config: ConvergenceConfig):
    return config.iterations()


def default_pre_loop_fn(config: ConvergenceConfig, iterations, polaris_inputs: PolarisInputs):
    if not config.results_dir.exists():
        config.results_dir.mkdir()

    transit_sql_file = Path(__file__).parent.parent / "sql" / "transit_stats.sql"
    logging.info(f"Running transit summary sql file: {transit_sql_file}")
    run_sql_file(transit_sql_file, polaris_inputs.supply_db)

    if config.add_rsus:
        RsuSampler(
            polaris_inputs.supply_db,
            config.rsu_highway_pr,
            config.rsu_major_pr,
            config.rsu_minor_pr,
            config.rsu_local_pr,
        ).generate_links_with_rsu_and_push()


def default_start_of_loop_fn(
    config: ConvergenceConfig, current_iteration: ConvergenceIteration, mods: dict, scenario_file: Path
):
    if current_iteration.is_dta:
        clean_db_for_dta(PolarisInputs.from_dir(config.data_dir, config.db_name))
    else:
        modelling_freight_deliveries = config.freight.should_model_deliveries(current_iteration)
        clean_db_for_abm(PolarisInputs.from_dir(config.data_dir, config.db_name), modelling_freight_deliveries)


def copy_back_files(config: ConvergenceConfig, current_iteration: ConvergenceIteration):  # pragma : no cover
    type = current_iteration.type()
    if type not in ("pop_synth", "cristal") and not (
        type == "skim" and (config.data_dir / config.highway_skim_file_name).exists()
    ):
        # If backup/highway_skim exists for skim, assume it's better than the free-flow skims we just produced here
        logging.info(f"    {type} iteration - copying back highway skim file")
        copy_replace_file(current_iteration.files.highway_skim, config.data_dir)
    if type == "skim":
        logging.info(f"    {type} iteration - copying back transit skim files")
        copy_replace_file(current_iteration.files.transit_skim, config.data_dir)
    if type != "skim":
        logging.info(f"    {type} iteration - copying back demand db")
        copy_replace_file(current_iteration.files.demand_db, config.data_dir)
    if type not in ("skim", "pop_synth", "cristal"):
        logging.info(f"    {type} iteration - copying back result db")
        copy_replace_file(current_iteration.files.result_db, config.data_dir)
        copy_replace_file(current_iteration.files.result_h5, config.data_dir)

    if config.freight.should_do_anything(current_iteration):
        logging.info(f"    {type} iteration - copying back freight db")
        copy_replace_file(current_iteration.files.freight_db, config.data_dir)


def default_end_of_loop_fn(
    config: ConvergenceConfig, current_iteration: ConvergenceIteration, output_dir: Path, polaris_inputs: PolarisInputs
):  # pragma : no cover
    logging.info("  Default End of Loop Function")

    generate_person_gaps(current_iteration.files.demand_db)
    copy_back_files(config, current_iteration)
    logging.info("    finished copying back files")

    copy_replace_file(polaris_inputs.supply_db, output_dir)

    aggregate_summaries(config.data_dir, save=True)
    record_stats_in_central_db(config, current_iteration)
    record_stats_locally(config, current_iteration)

    end_of_loop_fn_for_calibration(config, current_iteration, output_dir)


@can_fail
def record_stats_in_central_db(config: ConvergenceConfig, current_iteration: ConvergenceIteration):  # pragma : no cover
    engine = DbConfig.stats_db().create_engine()
    if engine is None:
        logging.info("Can't get a connection to the statistics DB - skipping")
        return
    record_statistics(config, current_iteration, engine)
    engine.dispose()


def engine_for(file):
    return create_engine(f"sqlite:///{file.absolute()}")


@can_fail
def record_stats_locally(config: ConvergenceConfig, current_iteration: ConvergenceIteration):  # pragma : no cover
    engine = engine_for(current_iteration.files.result_db)
    record_statistics(config, current_iteration, engine)

    # Additionally, record basic uuid info
    with commit_and_close(engine.connect()) as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS run_info(iteration_uuid str, convergence_uuid str);"))
        conn.execute(
            text("INSERT INTO run_info(iteration_uuid, convergence_uuid) VALUES(:iter,:config);"),
            {"iter": current_iteration.uuid, "config": config.uuid},
        )


def create_mep_outputs(output_dir: Path, output_files: PolarisInputs):  # pragma : no cover
    with commit_and_close((output_files.demand_db)) as conn:
        run_sql_file(
            sql_dir / "create_MEP_inputs.sql", conn, attach={"a": output_files.supply_db, "b": output_files.result_db}
        )
        run_sql_file(
            sql_dir / "calculate_VOT_adjusted_travel_times_no_adjustment.sql",
            conn,
            attach={"supply": output_files.supply_db, "result": output_files.result_db},
        )

        table_to_csv(conn, "link_MEP_calculations", output_dir / "network_results.csv")

        table_to_csv(conn, "activity_by_zone", output_dir / "activities.csv")
        table_to_csv(conn, "zone_parking", output_dir / "park_times.csv")
        table_to_csv(conn, "tnc_wait_times", output_dir / "tnc_wait_times.csv")


@can_fail
@function_logging("        ~   Running WTF analysis")
def run_wtf_analysis(config: ConvergenceConfig, current_iteration: ConvergenceIteration):
    run_baseline_analysis(current_iteration, config.population_scale_factor)


@can_fail
@function_logging("        ~   Pre-caching kpis")
def precache_kpis(current_iteration: ConvergenceIteration, kpis=KpiFilterConfig, skip_cache: bool = False):
    from polaris.analyze.result_kpis import ResultKPIs

    kpi = ResultKPIs.from_iteration(current_iteration, include_kpis=kpis.include_tags, exclude_kpis=kpis.exclude_tags)
    kpi.cache_all_available_metrics(skip_cache=skip_cache)


@can_fail
@function_logging("        ~   Running Charging analysis")
def run_charging_events_analysis(
    config: ConvergenceConfig, current_iteration: ConvergenceIteration
):  # pragma : no cover
    with commit_and_close(current_iteration.files.demand_db) as demand_conn:
        add_column_unless_exists(demand_conn, "EV_Charging", "x", "REAL")
        add_column_unless_exists(demand_conn, "EV_Charging", "y", "REAL")

        pop_scaling_factor = 1.0 / config.population_scale_factor
        # if we are writing all the ev vehicles traces, we only need to upfactor by the population sample rate
        if get_scenario_value(current_iteration.scenario_file, "EV_write_all_trajectories"):
            trajectory_factor = 1 / config.population_scale_factor
        else:
            # Otherwise we need to account for the lower sampling rate for traces
            if config.trajectory_sampling == 0:
                logging.info("Skipping charging event analysis as trajectory_sampling == 0")
                return
            trajectory_factor = 1 / config.trajectory_sampling

        sql_timings = run_sql_file(
            sql_dir / "charging_events.sql",
            demand_conn,
            attach={"a": current_iteration.files.supply_db},
            replacements={
                "xx_traj_scaling_factor_xx": trajectory_factor,
                "xx_pop_scaling_factor_xx": pop_scaling_factor,
            },
        )
        sql_timings.to_csv(current_iteration.output_dir / "charging_query_timing.tsv")


@function_logging("        ~ RUNNING in background thread for iteration {current_iteration}")
def default_async_fn(
    config: ConvergenceConfig, current_iteration: ConvergenceIteration, output_dir
):  # pragma : no cover
    run_wtf_analysis(config, current_iteration)
    if not current_iteration.is_skim:
        generate_gap_report(config, output_dir)

    run_charging_events_analysis(config, current_iteration)

    # Use the above data to store fast (to read) kpis
    if not current_iteration.is_skim:
        precache_kpis(current_iteration, config.kpis)

    copy_tables_to_stats_db(config, current_iteration)
    if not current_iteration.is_last:
        ScenarioCompression(output_dir).compress()


@can_fail
def copy_tables_to_stats_db(config: ConvergenceConfig, current_iteration: ConvergenceIteration):  # pragma : no cover
    tables_to_copy = [
        "vmt_vht_by_mode",
        "mode_Distribution_ADULT",
        "ttime_By_ACT_Average",
        "transit_vmt_pmt_occ_by_period",
    ]
    import pandas as pd

    engine = DbConfig.stats_db().create_engine()
    if engine is None:
        logging.info("Can't get a connection to the statistics DB - skipping")
        return
    with read_and_close(current_iteration.files.demand_db) as source_conn:
        for tbl in tables_to_copy:
            if not has_table(source_conn, tbl):
                logging.warning(f"Table {tbl} does not exist in the source database - skipping")
                continue
            df = pd.read_sql(f"SELECT * FROM {tbl}", source_conn)
            df = df.assign(iteration_uuid=current_iteration.uuid, convergence_uuid=config.uuid)
            df.to_sql(tbl, engine, if_exists="append", index=False)
    engine.dispose()


@can_fail
@function_logging("Deleting big files in {output_dir} and in sub-directories")
def delete_big_files(model_dir: Path):  # pragma : no cover
    """
    Runs a delete of all known "big" files in a model directory in a sequential manner. This is
    useful for avoiding a catestrophic bug in WSL that can crash the host and corrupt the image if
    too much data is deleted at once.
    -> https://github.com/microsoft/WSL/issues/7335
    """

    def foo(pattern):
        return (
            list(model_dir / f"*{pattern}")
            + list(model_dir / f"*{pattern}.tar.gz")
            + list(model_dir / "**" / f"*{pattern}")
            + list(model_dir / "**" / f"*{pattern}.tar.gz")
        )

    files_to_delete = foo("-Result.sqlite") + foo("highway_skim_file.bin") + foo("transit_skim_file.bin")
    for f in files_to_delete:
        logging.info(f"  - {f}")
        Path(f).unlink(missing_ok=True)
