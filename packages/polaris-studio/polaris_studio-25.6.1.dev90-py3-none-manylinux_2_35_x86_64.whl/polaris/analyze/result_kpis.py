# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

import logging
import re
import time
import traceback
from pathlib import Path
from shutil import rmtree
from typing import Tuple

import diskcache as dc  # type: ignore
import numpy as np
import pandas as pd
import psutil

from polaris.analyze.activity_metrics import ActivityMetrics
from polaris.analyze.kpi_utils import KPIFilter, kpi_type, KPITag, standard_kpis
from polaris.analyze.path_metrics import PathMetrics
from polaris.demand.demand import Demand
from polaris.runs.calibrate import (
    activity_generation,
    destination_choice,
    mode_choice,
    timing_choice,
    speed_by_funcl,
)
from polaris.runs.calibrate.utils import calculate_normalized_rmse
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.gap_reporting import load_gaps
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.polaris_version import parse_polaris_version
from polaris.runs.results.h5_results import H5_Results
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.runs.summary import load_summary
from polaris.runs.validate import count_validation
from polaris.runs.wtf_runner import render_wtf_file, render_sql, sql_dir
from polaris.utils.database.db_utils import (
    attach_to_conn,
    commit_and_close,
    has_table,
    read_and_close,
    read_table,
    run_sql,
    load_link_types,
)
from polaris.utils.database.standard_database import DatabaseType
from polaris.utils.dict_utils import denest_dict
from polaris.utils.file_utils import readlines
from polaris.utils.optional_deps import check_dependency


class ResultKPIs:
    """
    This class provides an easy way to extract relevant metrics for a single simulation run of POLARIS.
    The easiest way to generate an instance is via the factory method `from_iteration` which takes the path to the
    outputs of a simulation run (or a :func:`~Polaris.runs.convergence.ConvergenceIteration`)

    ::

        from polaris.analyze.result_kpi import ResultKPIs

        kpis = ResultKPIs.from_iteration(ref_project_dir / f"{city}_iteration_2")

    Metric comparison plots can then be generated in a notebook using:

    ::

        results = KpiComparator()
        results.add_run(kpis, 'an-arbitrary-label')
        results.plot_mode_share()
        results.plot_vmt()
        results.plot_vmt_by_link_type()

    Any number of runs can be added using `add_run` up to the limit of readability on the generated plots.
    """

    result_time_step = 3600

    def __init__(
        self,
        inputs: PolarisInputs,
        cache_dir: Path,
        population_scale_factor: float,
        include_kpis: Tuple[KPITag, ...],
        exclude_kpis: Tuple[KPITag, ...] = (
            KPITag.HIGH_MEMORY,
            KPITag.BROKEN,
        ),
    ):
        self.cache = self._load_cache(cache_dir)
        self._cache_dir = cache_dir
        self.inputs = inputs
        self.population_scale_factor = population_scale_factor
        self.__trip_data = pd.DataFrame([])
        self.__activity_data = pd.DataFrame([])
        self.__path_data = pd.DataFrame([])
        self.kpi_filter = KPIFilter(include_kpis, exclude_kpis)

    @classmethod
    def from_iteration(cls, iteration: ConvergenceIteration, **kwargs):
        """Create a KPI object from a ConvergenceIteration object."""
        if iteration.output_dir is None or iteration.files is None:
            raise RuntimeError("Given iteration doesn't have a defined output dir")
        return cls.from_args(iteration.files, iteration.output_dir, **kwargs)

    @classmethod
    def from_dir(cls, iteration_dir: Path, **kwargs):
        """Create a KPI object from a given directory."""
        if "db_name" in kwargs:
            inputs = PolarisInputs.from_dir(iteration_dir, db_name=kwargs["db_name"])
            del kwargs["db_name"]
        else:
            inputs = PolarisInputs.from_dir(iteration_dir)
        return cls.from_args(inputs, iteration_dir, **kwargs)

    @classmethod
    def from_args(
        cls,
        files: PolarisInputs,
        iteration_dir: Path,
        cache_name: str = "kpi.cache",
        clear_cache=False,
        exit_if_no_cache=False,
        population_scale_factor=None,
        include_kpis: Tuple[KPITag, ...] = standard_kpis,
        exclude_kpis: Tuple[KPITag, ...] = (KPITag.HIGH_MEMORY, KPITag.BROKEN),
    ):
        cache_dir = Path(iteration_dir) / cache_name
        if cache_dir.exists() and clear_cache:
            rmtree(cache_dir)

        if population_scale_factor is None:
            population_scale_factor = ConvergenceConfig.from_dir(iteration_dir).population_scale_factor

        if not cache_dir.exists() and exit_if_no_cache:
            return None

        return cls(files, cache_dir, population_scale_factor, include_kpis=include_kpis, exclude_kpis=exclude_kpis)

    def _load_cache(self, cache_dir) -> dc.Cache:
        if cache_dir is None:
            return None

        # make sure we never leave open connections to the cache lying around
        def create_and_close(cache_dir_):
            c = dc.Cache(cache_dir_)
            c.close()
            return c

        try:
            return create_and_close(cache_dir)
        except Exception:
            (Path(cache_dir) / "cache.db").unlink(missing_ok=True)
            return create_and_close(cache_dir)

    def cache_all_available_metrics(self, verbose=1, metrics_to_cache=None, skip_cache=False):
        metrics_to_cache = self.available_metrics() if metrics_to_cache is None else set(metrics_to_cache)
        metrics_to_cache = (m for m in metrics_to_cache if self.kpi_filter.allows(m))

        durations = {}
        total_start_time = time.time()
        for m in metrics_to_cache:
            start_time = time.time()
            try:
                verbose > 1 and logging.info(f"            => {m}")
                self.get_cached_kpi_value(m, skip_cache=skip_cache)
                memory_info = psutil.Process().memory_info()
                verbose > 1 and logging.info(f"               {memory_info.rss / (1024 ** 2):.2f} MB")
            except Exception:
                logging.warning(f"failed: {m}")
                if verbose >= 1:
                    tb = traceback.format_exc()
                    print(tb, flush=True)
            durations[m] = round(time.time() - start_time, 1)

        self.cache.close()

        # Timing report
        logging.info(f"Saving precaching KPIs runtime report, total time: {round(time.time() - total_start_time, 1)}s")
        df = pd.DataFrame(data=list(durations.items()), columns=["metric name", "duration (s)"])
        df.to_csv(self._cache_dir / "cache_all_metric_timing.csv", index=False)

    @classmethod
    def available_metrics(self):
        return {e.replace("metric_", "") for e in dir(self) if e.startswith("metric_")}

    def close(self):
        self.cache.close()

    def get_kpi_value(self, kpi_name):
        attr_name = f"metric_{kpi_name}"
        if hasattr(self, attr_name) and callable(self.__getattribute__(attr_name)):
            return self.__getattribute__(attr_name)()
        raise RuntimeError(f"it seems we don't have a way to compute: {kpi_name}")

    def get_cached_kpi_value(self, kpi_name, skip_cache=False, force_cache=False):
        try:
            if self.cache is None:
                return self.get_kpi_value(kpi_name)

            def generate():
                logging.debug(f"Generating KPI value {kpi_name}")
                self.cache.set(kpi_name, self.get_kpi_value(kpi_name))

            if skip_cache:
                generate()
            elif kpi_name not in self.cache:
                if force_cache:
                    return None
                generate()

            return self.cache.get(kpi_name)
        finally:
            # Any time we read or write to the cache - we need to close it!
            self.cache.close()

    def has_cached_kpi(self, kpi_name):
        try:
            return self.cache is not None and kpi_name in self.cache
        finally:
            # Any time we read or write to the cache - we need to close it!
            self.cache.close()

    def cached_metrics(self):
        try:
            return set() if self.cache is None else set(self.cache.iterkeys())
        finally:
            # Any time we read or write to the cache - we need to close it!
            self.cache.close()

    @kpi_type(KPITag.SYSTEM)
    def metric_summary(self):
        return load_summary(self.inputs.summary, raise_on_error=False)

    @kpi_type(KPITag.SYSTEM)
    def metric_file_sizes(self):
        iter_dir = self.inputs.result_h5.parent

        def f(pattern):
            files = list(iter_dir.glob(f"*{pattern}*"))
            if len(files) == 1:
                return (files[0].name, files[0].stat().st_size)
            logging.info(f"Can't find a file matching pattern: {pattern}")
            return None

        file_sizes = ["Supply.sqlite", "Demand.sqlite", "Result.sqlite", "Result.h5", "Freight.sqlite"]
        file_sizes = [f(e) for e in file_sizes]
        return pd.DataFrame([e for e in file_sizes if e], columns=["filename", "filesize"])

    @kpi_type(KPITag.SYSTEM)
    def metric_polaris_exe(self):
        log_head = readlines(self._cache_dir.parent / "log" / "polaris_progress.log", 30)
        branch, sha, build_date = parse_polaris_version("\n".join(log_head))
        url = f"https://git-out.gss.anl.gov/polaris/code/polaris-linux/-/commit/{sha}"
        return pd.DataFrame({"branch": [branch], "sha": [sha], "build_date": [build_date], "url": [url]})

    @kpi_type(KPITag.CONVERGENCE)
    def metric_gaps(self):
        return load_gaps(self.inputs.gap)

    @staticmethod
    def one_value(conn, query, default=0):
        return conn.execute(query).fetchone()[0] or default

    @kpi_type(KPITag.POPULATION)
    def metric_population(self):
        columns = ["num_persons", "num_adults", "num_employed"]
        where_clauses = ["1==1", "person.age > 16", "work_location_id > 1"]
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            vals = [
                ResultKPIs.one_value(
                    conn, render_sql(f"SELECT count(*) FROM person WHERE {w};", self.population_scale_factor)
                )
                for w in where_clauses
            ]
            return pd.DataFrame([vals], columns=columns)

    @kpi_type(KPITag.POPULATION)
    def metric_num_persons_by_age_band_5(self):
        return self._metric_num_persons_by_age_band_x(5)

    @kpi_type(KPITag.POPULATION)
    def metric_num_persons_by_age_band_10(self):
        return self._metric_num_persons_by_age_band_x(10)

    def _metric_num_persons_by_age_band_x(self, x):
        query = f""" SELECT {x} * (person.age / {x}) as bucket, count(*) * scaling_factor as count
                     FROM person
                     GROUP BY (person.age / {x}); """
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            return pd.read_sql(render_sql(query, self.population_scale_factor), conn)

    @kpi_type((KPITag.POPULATION, KPITag.SCALAR))
    def metric_num_hh(self):
        query = """ SELECT count(*) * scaling_factor as num_hh
                    FROM household;"""
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            return conn.execute(render_sql(query, self.population_scale_factor)).fetchone()[0] or 0

    @kpi_type(KPITag.POPULATION)
    def metric_num_hh_by_hh_size(self):
        query = """ SELECT q.hh_size, count(*) * scaling_factor as num_hh
                     FROM (SELECT person.household, count(*) as hh_size
                           FROM person
                           GROUP BY person.household) as q
                     GROUP BY q.hh_size;"""
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            return pd.read_sql(render_sql(query, self.population_scale_factor), conn)

    @kpi_type((KPITag.TRIPS, KPITag.SCALAR))
    def metric_tts(self):
        # If Trip table is empty we return 0 as the execute.fetchone()[0] will return None
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            return conn.execute('SELECT SUM(end-start) from trip WHERE "end">"start"').fetchone()[0] or 0

    @kpi_type(KPITag.ACTIVITIES)
    def metric_distance_by_act_type(self):
        query = """ SELECT activity.type as acttype, avg(trip.travel_distance)/1609.3 as dist_avg
                    FROM trip
                    JOIN person ON trip.person = person.person
                    JOIN household ON person.household = household.household
                    JOIN activity ON activity.trip = trip.trip_id
                    WHERE person.age > 16
                      AND trip.end - trip.start > 0
                      AND trip.end - trip.start < 10800
                    GROUP BY ACTTYPE; """
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            return pd.read_sql(query, conn)

    @kpi_type(KPITag.ACTIVITIES_PLANNED)
    def metric_planned_modes(self):
        query = """Select activity.mode, count(*) as mode_count
                   FROM activity
                            JOIN person ON activity.person = person.person
                   WHERE activity.start_time > 122
                     and activity.trip = 0
                     and person.age > 16
                   GROUP BY activity.mode"""
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            return pd.read_sql(query, conn)

    @kpi_type(KPITag.ACTIVITIES)
    def metric_executed_modes(self):
        query = """Select activity.mode, count(*) as mode_count
                   FROM activity JOIN person ON activity.person = person.person
                   WHERE activity.start_time > 122 and activity.trip <> 0 and person.age > 16
                   GROUP BY activity.mode"""
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            return pd.read_sql(query, conn)

    @kpi_type(KPITag.TRIPS)
    def metric_mode_shares(self):
        df = self._add_mode_names(self._slow_fast(sql_dir / "mode_share.template.sql", "mode_distribution_adult"))

        cols = ["HBW", "HBO", "NHB", "total"]
        df[[f"{c}_pr" for c in cols]] = df[cols] / df[cols].sum()
        return df

    def _add_mode_names(self, df):
        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            mode_lookup = Demand.load_modes(conn)
        df["mode"] = df["mode"].apply(lambda m: mode_lookup.get(m, f"{m}_Unknown"))
        return df

    @kpi_type(KPITag.ACTIVITIES)
    def metric_executed_activity_mode_share_by_income(self):
        sql = """
            Select
                income_quintile_fn as INCOME_QUINTILE,
                sum (case when activity.mode in (transit_modes) then 1.0 else 0.0 end)/(count(*) + 0.0) as transit_share,
                sum (case when activity.mode in ('TAXI') then 1.0 else 0.0 end)/(count(*) + 0.0) as tnc_share,
                sum (case when activity.mode in ('SOV', 'HOV') then 1.0 else 0.0 end)/(count(*) + 0.0) as auto_share,
                sum (case when activity.mode in ('WALK', 'BIKE') then 1.0 else 0.0 end)/(count(*) + 0.0) as active_share,
                sum (case when activity.mode not in (transit_modes, 'TAXI', 'SOV', 'HOV', 'WALK', 'BIKE') then 1.0 else 0.0 end)/(count(*) + 0.0) as other_share
            FROM
                activity, person, trip, household
            WHERE
                activity.start_time > 122 and
                activity.trip = trip.trip_id and
                trip."end" - trip."start" > 2 and
                activity.person = person.person and
                person.household = household.household and
                activity.mode not like 'FAIL%'
            GROUP BY
                INCOME_QUINTILE;
        """
        return self._slow_fast(sql, "executed_activity_mode_share_by_income")

    @kpi_type(KPITag.ACTIVITIES)
    def metric_activity_start_distribution(self):
        return self._slow_fast(sql_dir / "activity_start_distribution.template.sql", "Activity_Start_Distribution")

    @kpi_type(KPITag.ACTIVITIES)
    def metric_activity_rate_distribution(self):
        return self._slow_fast(sql_dir / "activity_distribution.template.sql", "activity_rate_distribution")

    @kpi_type(KPITag.ACTIVITIES)
    def metric_activity_duration_distribution(self):
        sql = """
            SELECT
                type as act_type,
                cast(start_time/3600 as int) as start_time,
                avg(duration) as average_duration,
                scaling_factor * count(*) as num_activities
            FROM Activity
            WHERE start_time > 122 and trip <> 0
            GROUP BY 1,2;
        """
        return self._slow_fast(sql, "Activity_Duration_Distribution")

    @kpi_type(KPITag.TRAFFIC)
    def metric_vmt_vht(self):
        sql_slow = """
            SELECT mode,
                   scaling_factor*sum(travel_distance)/1609.3/1000000.0 as million_VMT,
                   scaling_factor*sum(end-start)/3600.0/1000000.0 as million_VHT,
                   sum(travel_distance)/1609.3 / (sum(end-start)/3600.0) as speed_mph,
                   scaling_factor*count(*) as count
            FROM trip
            WHERE "end" > "start"
            AND (
                    (mode IN (0,9) AND has_artificial_trip <> 1)  -- skip stuck auto trips
                 OR (mode NOT IN (0,9))                           -- non-auto modes
            )
            GROUP BY mode;
        """
        return self._add_mode_names(self._slow_fast(sql_slow, "vmt_vht_by_mode")).set_index("mode")

    @kpi_type(KPITag.VEHICLES)
    def metric_ev_charging(self):
        sql = """
            SELECT
                "Location_Type",
                "is_tnc_vehicle",
                scaling_factor * sum("Energy_Out_Wh"- "Energy_In_Wh")/1000000.0 as total_energy_charged_MWh,
                scaling_factor * sum(Time_Start - Time_In)/3600.0 as total_wait_hours,
                scaling_factor * sum(Time_Out - Time_Start)/3600.0 as total_charge_hours,
                scaling_factor * sum(charged_money) as total_charged_dollars,
                scaling_factor * sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as positive_charge_count,
                scaling_factor * count(*) as charge_count,
                sum("Energy_Out_Wh"- "Energy_In_Wh")/1000.0/sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as average_energy_charged_kWh,
                sum(Time_Start - Time_In)/60.0/count(*) as average_wait_minutes,
                sum(Time_Out - Time_Start)/60.0/sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as average_charge_minutes,
                sum(charged_money)/sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as average_paid_dollars_per_event,
                sum(charged_money)*1000.0/sum("Energy_Out_Wh"- "Energy_In_Wh") as averaged_paid_dollars_per_kWh
            FROM "EV_Charging"
            group BY 1,2;
        """
        return self._slow_fast(sql, "ev_charge_summary_2")

    @kpi_type(KPITag.TRAFFIC)
    def metric_vmt_vht_by_link(self):
        if not self.inputs.result_h5.exists():
            logging.warning("No H5 file to process")
            return

        h5_results = H5_Results(ScenarioCompression.maybe_extract(self.inputs.result_h5))
        vmt_vht = h5_results.get_vmt_vht(self.population_scale_factor)
        return pd.concat([load_link_types(self.inputs.supply_db), vmt_vht], axis=1)

    @kpi_type(KPITag.TRAFFIC)
    def metric_flow_density_fd(self):
        if not self.inputs.result_h5.exists():
            logging.warning("No H5 file to process")
            return

        # I guess we can load h5 just once at the ResultKPIs class level?
        h5_results = H5_Results(ScenarioCompression.maybe_extract(self.inputs.result_h5))
        flow_density = h5_results.get_flow_density()
        df = (
            pd.concat([load_link_types(self.inputs.supply_db), flow_density], axis=1)
            .drop(columns=["zone"])
            .reset_index()
        )

        df_dens = df.melt(
            id_vars=["linknr", "type"],
            value_name="density",
            var_name="time_step",
            value_vars=[x for x in df.columns if "density" in x],
        )
        df_dens.time_step = df_dens.time_step.str.replace("density_", "")

        df_flow = df.melt(
            id_vars=["linknr", "type"],
            value_name="flow",
            var_name="time_step",
            value_vars=[x for x in df.columns if "flow" in x],
        )
        df_flow.time_step = df_flow.time_step.str.replace("flow_", "")

        df_merge = pd.merge(left=df_dens, right=df_flow, on=["linknr", "time_step"])
        # Drop NA to be removed after fixing h5
        df_merge = df_merge.replace(np.Inf, np.NaN).dropna()
        df_merge["density_bin"] = (df_merge.density / 0.1).astype(int) * 0.1
        df_fd = df_merge.groupby(["type_x", "density_bin"]).agg({"flow": "max"})
        df_fd = df_fd.reset_index()

        return df_fd

    @kpi_type(KPITag.ACTIVITIES)
    def metric_activity_distances(self):
        return self._slow_fast(
            sql_dir / "travel_time.template.sql", "ttime_By_ACT_Average", attach_db_type=DatabaseType.Supply
        )

    @kpi_type(KPITag.VEHICLES)
    def metric_vehicle_technology(self):
        sql = """
            SELECT (CASE WHEN v.hhold > 0 THEN 1 ELSE v.hhold END) as agent_type, vc.class_type,
                   ct.type as connected, at.type as automation_level, pt.type as powertrain_type, count(*) as veh_count
            from vehicle v, vehicle_type vt, vehicle_class vc, connectivity_type ct, automation_type at, powertrain_type pt
            WHERE v.type = vt.type_id
            AND vt.vehicle_class = vc.class_id
            AND vt.connectivity_type = ct.type_id
            AND at.type_id = vt.automation_type
            AND pt.type_id = vt.powertrain_type
            GROUP BY 1,2,3,4,5;
        """
        return self._slow_fast(sql, "vehicle_technology")

    def _slow_fast(self, slow_sql, table_name, db_type=DatabaseType.Demand, attach_db_type=None):
        """Utility method to read analytics data from table. Uses slow query to create it if table doesn't exist."""
        with commit_and_close(ScenarioCompression.maybe_extract(self._get_db(db_type))) as conn:
            if has_table(conn, table_name):
                return pd.read_sql(sql=f"SELECT * FROM {table_name};", con=conn)
            if attach_db_type is not None:
                attach_to_conn(conn, {"a": ScenarioCompression.maybe_extract(self._get_db(attach_db_type))})

            # If the given input is a path to a template file, or a create table statement, just run it
            if isinstance(slow_sql, Path):
                run_sql(render_wtf_file(slow_sql, self.population_scale_factor), conn)
            elif re.match("create table", slow_sql.lower()):
                run_sql(slow_sql, conn)
            else:
                # Otherwise wrap it up into a create table to cache the result
                conn.execute(f"CREATE TABLE {table_name} AS {render_sql(slow_sql, self.population_scale_factor)}")
            return pd.read_sql(sql=f"SELECT * FROM {table_name};", con=conn)

    def _get_db(self, db_type: DatabaseType):
        if db_type == DatabaseType.Demand:
            return self.inputs.demand_db
        if db_type == DatabaseType.Supply:
            return self.inputs.supply_db
        if db_type == DatabaseType.Results:
            return self.inputs.result_db

    @kpi_type(KPITag.TNC)
    def metric_tnc_request_stats(self):
        return self._slow_fast(sql_dir / "tnc.template.sql", "tnc_request_stats")

    @kpi_type(KPITag.TNC)
    def metric_tnc_trip_stats(self):
        return self._slow_fast(sql_dir / "tnc.template.sql", "tnc_trip_stats")

    @kpi_type(KPITag.TNC)
    def metric_tnc_stats(self):
        return self._slow_fast(sql_dir / "on_result" / "tnc.template.sql", "tnc_stats", DatabaseType.Results)

    @kpi_type(KPITag.TNC)
    def metric_avo_by_tnc_operator(self):
        return self._slow_fast(sql_dir / "tnc.template.sql", "avo_by_tnc_operator")

    @kpi_type(KPITag.TRAFFIC)
    def metric_road_pricing(self):
        return self._slow_fast(sql_dir / "wtf_baseline_analysis.template.sql", "toll_revenue")

    @kpi_type(KPITag.TRANSIT)
    def metric_transit_boardings(self):
        sql_slow = """
            SELECT
                ta.agency as agency,
                transit_mode_fn as "mode",
                scaling_factor*sum(tvl.value_boardings) as boardings,
                scaling_factor*sum(tvl.value_alightings) as alightings
            FROM
                "Transit_Vehicle_links" tvl,
                transit_vehicle tv,
                a.transit_trips tt,
                a.transit_patterns tp,
                a.transit_routes tr,
                a.transit_agencies ta
            where
                tvl.value_transit_vehicle_trip = tv.transit_vehicle_trip and
                tvl.value_transit_vehicle_trip = tt.trip_id and
                tp.pattern_id = tt.pattern_id and
                tr.route_id = tp.route_id AND
                tr.agency_id = ta.agency_id
            group by
                ta.agency,
                tv.mode
            order by
                ta.agency,
                tv.mode desc
            ;
        """
        return self._slow_fast(sql_slow, "boardings_by_agency_mode", attach_db_type=DatabaseType.Supply)

    @kpi_type(KPITag.TRANSIT)
    def metric_transit_experience(self):
        paths = H5_Results(self.inputs.result_h5).get_mm_paths()
        paths["wait_time"] = paths.actual_bus_wait_time + paths.actual_rail_wait_time + paths.actual_comm_rail_wait_time
        paths["ivtt"] = paths.actual_bus_ivtt + paths.actual_rail_ivtt + paths.actual_comm_rail_ivtt
        df = paths.groupby("mode").agg(
            {
                "timestep": "count",
                "actual_duration": "mean",
                "actual_wait_count": "mean",
                "actual_tnc_wait_count": "mean",
                "wait_time": "mean",
                "actual_tnc_wait_time": "mean",
                "ivtt": "mean",
                "actual_walk_time": "mean",
                "actual_bike_time": "mean",
                "actual_car_time": "mean",
                "actual_monetary_cost": "mean",
            }
        )
        renames = {k: k.replace("actual_", "") for k in df.columns if k.startswith("actual_")}
        df = df.rename(columns={"timestep": "count"} | renames)
        return df.reset_index()

    def network_gaps_by_x(self, x):
        dfs = []
        h5_results = H5_Results(ScenarioCompression.maybe_extract(self.inputs.result_h5))
        link_attrs = read_table("link", ScenarioCompression.maybe_extract(self.inputs.supply_db))
        link_attrs = link_attrs[["link", "length", "type"]]
        link_attrs["total_dist"] = link_attrs["length"] / 1609.0
        link_attrs = link_attrs.rename(columns={"type": "link_type"})

        for t in h5_results.timesteps:
            df = h5_results.get_path_links_for_timestep(t)
            df = df[df["travel_time"] > 0]
            df["tt_diff"] = df.travel_time - df.routed_travel_time
            df["tt_diff_abs"] = abs(df.travel_time - df.routed_travel_time)
            df["hour"] = (df["entering_time"] / 3600).astype(int)
            df = df[["hour", "link_id", "routed_travel_time", "tt_diff", "tt_diff_abs"]]
            df = pd.merge(df, link_attrs, left_on="link_id", right_on="link")

            df = df[[x, "total_dist", "routed_travel_time", "tt_diff", "tt_diff_abs"]]
            df = df.groupby(x).sum().reset_index()
            dfs.append(df)

        df = pd.concat(dfs).groupby(x).sum().reset_index()
        df["abs_gap"] = df["tt_diff_abs"] / df["routed_travel_time"]
        df["gap"] = df["tt_diff"] / df["routed_travel_time"]
        df = df[[x, "total_dist", "abs_gap", "gap"]]
        return df.sort_values(by=x, axis=0)

    @kpi_type(KPITag.CONVERGENCE)
    def metric_network_gaps_by_link_type(self):
        return self.network_gaps_by_x("link_type")

    @kpi_type(KPITag.CONVERGENCE)
    def metric_network_gaps_by_hour(self):
        return self.network_gaps_by_x("hour")

    @kpi_type((KPITag.SKIMS, KPITag.HIGH_MEMORY))
    def metric_skim_stats(self):
        check_dependency("openmatrix")
        from polaris.skims.highway.highway_skim import HighwaySkim
        from polaris.skims.transit.transit_skim import TransitSkim

        hwy_skim = HighwaySkim.from_file(self.inputs.highway_skim)
        pt_skim_file = self.inputs.transit_skim
        if not pt_skim_file.exists():
            logging.debug(f"Skipping Transit skim metrics as file ({pt_skim_file}) not found")
            pt_skim = None
        else:
            pt_skim = TransitSkim.from_file(pt_skim_file)

        def f(skims, mode, interval, metric):
            mat = skims.get_skims(metric=metric, mode=mode, interval=interval)
            isfinite_mask = np.isfinite(mat)
            return {
                "interval": interval,
                "metric": metric,
                "mode": mode,
                "min": np.nanmin(mat[(mat > 0) & isfinite_mask], initial=0),
                "max": np.nanmax(mat[isfinite_mask], initial=10000),
                "avg": np.nanmean(mat[isfinite_mask]),
                # "std": mat[isfinite_mask].std(initial=10000),
            }

        df = pd.DataFrame([f(hwy_skim, "Auto", i, j) for i in hwy_skim.intervals for j in ["time", "distance"]])
        if pt_skim is None:
            return df

        df_transit = pd.DataFrame(
            [f(pt_skim, m, i, j) for i in pt_skim.intervals for j in ["time"] for m in ["Bus", "Rail"]]
        )
        return pd.concat([df, df_transit])

    @kpi_type(KPITag.VALIDATION)
    def metric_count_validation(self):
        targets_dir = self._get_target_dir()
        target, periods = count_validation.load_targets(targets_dir / "link_volume_targets.csv")
        if target is None:
            return None
        simulated = count_validation.load_simulated(self.inputs.result_h5, self.population_scale_factor, periods)
        link_attrs = read_table("link", ScenarioCompression.maybe_extract(self.inputs.supply_db))
        df = link_attrs.set_index("link")[["type"]]
        return df.join(target).join(simulated).reset_index()

    def _get_target_dir(self):
        targets_dir = ConvergenceConfig.from_dir(self.inputs.demand_db.parent).calibration.target_csv_dir
        if not targets_dir.exists():
            logging.warning(f"No calibration targets found {targets_dir}")
            return None
        return targets_dir

    def _get_simulated_and_target_dict(self, target_type: str, use_planned=False, **kwargs):
        targets_dir = self._get_target_dir()

        if target_type == "activity_generation":
            simulated = activity_generation.load_simulated(self.inputs.demand_db, use_planned)
            target = activity_generation.load_target(targets_dir / "activity_generation_targets.csv")
        elif target_type == "mode_choice":
            simulated = mode_choice.load_simulated(self.inputs, self.population_scale_factor, use_planned)
            target = mode_choice.load_targets(targets_dir / "mode_choice_targets.csv")
        elif target_type == "destination_choice":
            data_type = kwargs.get("data_type", "distance")
            simulated = destination_choice.load_simulated(
                self.inputs.demand_db, self.inputs.supply_db, data_type=data_type
            )
            target = destination_choice.load_target(targets_dir / "destination_choice_targets.csv", data_type=data_type)
        elif target_type == "mode_choice_boardings":
            target_file = targets_dir / "mode_choice_boarding_targets.csv"
            if not target_file.exists():
                return None, None
            simulated = mode_choice.load_simulated_boardings(self.inputs, self.population_scale_factor)
            target = mode_choice.load_target_boardings(target_file)
        elif target_type == "timing":
            simulated = timing_choice.load_simulated(self.inputs, self.population_scale_factor, use_planned)
            target = timing_choice.load_target(targets_dir / "timing_choice_targets.csv")
        elif target_type == "speed_by_funcl":
            simulated = speed_by_funcl.load_simulated(self.inputs, self.population_scale_factor)
            target = speed_by_funcl.load_target(targets_dir / "speed_by_funcl_targets.csv")
        else:
            logging.error(f"Calibration targets not implemented for {target_type}")

        return simulated, target

    @kpi_type(KPITag.VALIDATION)
    def metric_rmse_vs_observed(self):
        columns = ["RMSE_activity", "RMSE_mode", "RMSE_mode_boardings", "RMSE_destination", "RMSE_timing"]

        if self._get_target_dir() is None:
            return pd.DataFrame(data=[[-1, -1, -1, -1, -1]], columns=columns)

        simulated, target = self._get_simulated_and_target_dict("activity_generation")
        rmse_activity = calculate_normalized_rmse({k: r for k, (r, _) in simulated.items()}, target)

        simulated, target = self._get_simulated_and_target_dict("destination_choice")
        rmse_destination = calculate_normalized_rmse(simulated, target)

        simulated, target = self._get_simulated_and_target_dict("mode_choice")
        rmse_mode = calculate_normalized_rmse(denest_dict(simulated), denest_dict(target))

        simulated, target = self._get_simulated_and_target_dict("mode_choice_boardings")
        rmse_boardings = calculate_normalized_rmse(simulated, target)

        simulated, target = self._get_simulated_and_target_dict("timing")
        rmse_timing = calculate_normalized_rmse(denest_dict(simulated), denest_dict(target))

        return pd.DataFrame(
            data=[[rmse_activity, rmse_mode, rmse_boardings, rmse_destination, rmse_timing]], columns=columns
        )

    @kpi_type(KPITag.ACTIVITIES_PLANNED)
    def metric_planned_rmse_vs_observed(self):
        columns = ["RMSE_activity", "RMSE_mode", "RMSE_timing"]

        if self._get_target_dir() is None:
            return pd.DataFrame(data=[[-1, -1, -1]], columns=columns)

        simulated, target = self._get_simulated_and_target_dict("activity_generation", use_planned=True)
        rmse_activity = calculate_normalized_rmse({k: r for k, (r, _) in simulated.items()}, target)

        simulated, target = self._get_simulated_and_target_dict("mode_choice", use_planned=True)
        rmse_mode = calculate_normalized_rmse(denest_dict(simulated), denest_dict(target))

        simulated, target = self._get_simulated_and_target_dict("timing", use_planned=True)
        rmse_timing = calculate_normalized_rmse(denest_dict(simulated), denest_dict(target))

        return pd.DataFrame(data=[[rmse_activity, rmse_mode, rmse_timing]], columns=columns)

    @kpi_type(KPITag.CALIBRATION)
    def metric_calibration_act_gen(self):
        columns = ["pertype", "acttype", "target", "simulated", "per_count"]

        if self._get_target_dir() is None:
            return

        simulated, target = self._get_simulated_and_target_dict("activity_generation")

        keys = set.intersection(set(target.keys()), set(simulated.keys()))
        act_gen_df = pd.DataFrame([(key[0], key[1], target[key], *simulated[key]) for key in keys], columns=columns)
        act_gen_df.set_index(["pertype", "acttype"], inplace=True)

        return act_gen_df

    @kpi_type(KPITag.ACTIVITIES_PLANNED)
    def metric_calibration_act_gen_planned(self):
        columns = ["pertype", "acttype", "simulated", "target", "per_count"]

        if self._get_target_dir() is None:
            return

        simulated, target = self._get_simulated_and_target_dict("activity_generation", use_planned=True)

        keys = set.intersection(set(target.keys()), set(simulated.keys()))
        act_gen_df = pd.DataFrame([(key[0], key[1], target[key], *simulated[key]) for key in keys], columns=columns)
        act_gen_df.set_index(["pertype", "acttype"], inplace=True)

        return act_gen_df

    @kpi_type(KPITag.CALIBRATION)
    def metric_calibration_mode_share(self):
        columns = ["type", "mode", "simulated", "target"]
        if self._get_target_dir() is None:
            return

        simulated, target = self._get_simulated_and_target_dict("mode_choice")

        mode_choice_df = pd.DataFrame(columns=columns)
        for key_type in set.intersection(set(target.keys()), set(simulated.keys())):
            for key_mode in set.intersection(set(target[key_type].keys()), set(simulated[key_type].keys())):
                mode_choice_df.loc[len(mode_choice_df.index)] = [
                    key_type,
                    key_mode,
                    simulated[key_type][key_mode],
                    target[key_type][key_mode],
                ]

        return mode_choice_df

    @kpi_type(KPITag.ACTIVITIES_PLANNED)
    def metric_calibration_mode_share_planned(self):
        columns = ["type", "mode", "simulated", "target"]
        if self._get_target_dir() is None:
            return

        simulated, target = self._get_simulated_and_target_dict("mode_choice", use_planned=True)

        mode_choice_df = pd.DataFrame(columns=columns)
        for key_type in set.intersection(set(target.keys()), set(simulated.keys())):
            for key_mode in set.intersection(set(target[key_type].keys()), set(simulated[key_type].keys())):
                mode_choice_df.loc[len(mode_choice_df.index)] = [
                    key_type,
                    key_mode,
                    simulated[key_type][key_mode],
                    target[key_type][key_mode],
                ]

        return mode_choice_df

    @kpi_type(KPITag.CALIBRATION)
    def metric_calibration_timing(self):
        columns = ["act_type", "period", "target", "simulated"]
        if self._get_target_dir() is None:
            return

        simulated, target = self._get_simulated_and_target_dict("timing")

        timing_df = pd.DataFrame(columns=columns)
        for key_type in set.intersection(set(target.keys()), set(simulated.keys())):
            for key_period in set.intersection(set(target[key_type].keys()), set(simulated[key_type].keys())):
                timing_df.loc[len(timing_df.index)] = [
                    key_type,
                    key_period,
                    target[key_type][key_period],
                    simulated[key_type][key_period],
                ]

        return timing_df

    @kpi_type(KPITag.ACTIVITIES_PLANNED)
    def metric_calibration_timing_planned(self):
        columns = ["act_type", "period", "target", "simulated"]
        if self._get_target_dir() is None:
            return

        simulated, target = self._get_simulated_and_target_dict("timing", use_planned=True)

        timing_df = pd.DataFrame(columns=columns)
        for key_type in set.intersection(set(target.keys()), set(simulated.keys())):
            for key_period in set.intersection(set(target[key_type].keys()), set(simulated[key_type].keys())):
                timing_df.loc[len(timing_df.index)] = [
                    key_type,
                    key_period,
                    target[key_type][key_period],
                    simulated[key_type][key_period],
                ]

        return timing_df

    @kpi_type(KPITag.CALIBRATION)
    def metric_calibration_destination(self):
        columns = ["acttype", "data_type", "target", "simulated"]
        if self._get_target_dir() is None:
            return

        simulated, target = self._get_simulated_and_target_dict("destination_choice")
        simulated_time, target_time = self._get_simulated_and_target_dict(
            target_type="destination_choice", data_type="travel_time"
        )
        keys = set.intersection(set(target.keys()), set(simulated.keys()))
        return pd.DataFrame(
            [(key, "distance", target[key], simulated[key]) for key in keys]
            + [(key, "travel_time", target_time[key], simulated_time[key]) for key in keys],
            columns=columns,
        )

    @kpi_type(KPITag.CALIBRATION)
    def metric_calibration_boardings(self):
        columns = ["agency", "mode", "target", "simulated"]
        if self._get_target_dir() is None:
            return

        simulated, target = self._get_simulated_and_target_dict("mode_choice_boardings")
        if simulated is None or target is None:
            return

        keys = set.intersection(set(target.keys()), set(simulated.keys()))
        return pd.DataFrame([(key[0], key[1], target[key], simulated[key]) for key in keys], columns=columns)

    @kpi_type(KPITag.VALIDATION)
    def metric_validation_speed(self):
        columns = ["link_type", "time_period", "target", "simulated"]

        if self._get_target_dir() is None:
            logging.warning("No calibration target directory")
            return

        simulated, target = self._get_simulated_and_target_dict("speed_by_funcl")
        if simulated is None or target is None:
            logging.warning("No target and simulation data")
            return

        keys = set.intersection(set(target.keys()), set(simulated.keys()))
        return pd.DataFrame([(key[0], key[1], target[key], simulated[key]) for key in keys], columns=columns)

    @kpi_type(KPITag.TRIPS)
    def metric_trip_length_distribution(self):
        sql = """SELECT travel_distance
                   FROM Trip t
                  WHERE t.mode IN (0, 9, 17, 18, 19, 20)
                    AND t.has_artificial_trip <> 1 and t.start>=0
                    AND t.end<=110000
                    AND t.end > t.start
                    AND t.routed_travel_time > 0
                    AND t.travel_distance>0;"""

        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            df = pd.read_sql(sql, conn)
        max_dist = min(120, int(df.travel_distance.max() / 1000))

        y, x = np.histogram(df.travel_distance.to_numpy() / 1000, bins=range(0, max_dist))
        return pd.DataFrame({"distance": x[1:], "trips": y})

    @kpi_type(KPITag.ACTIVITIES)
    def metric_activity_start_time_distributions(self):
        sql = """SELECT start as tstart
                   FROM Trip t
                  WHERE t.mode IN (0, 9, 17, 18, 19, 20)
                    AND t.has_artificial_trip <> 1 and t.start>=0
                    AND t.end<=110000
                    AND t.end > t.start
                    AND t.routed_travel_time > 0"""

        with read_and_close(ScenarioCompression.maybe_extract(self.inputs.demand_db)) as conn:
            df = pd.read_sql(sql, conn)

        # ~ 1000 trips per bin on average worked well for both Bloomington and Austin
        bins = int(max(30, np.floor(df.shape[0] / 1000)))
        y, x = np.histogram(df.tstart.to_numpy(), bins=bins)
        return pd.DataFrame({"trip_start": x[1:], "trips": y})

    @kpi_type((KPITag.ACTIVITIES_PLANNED, KPITag.HIGH_MEMORY))
    def metric_planned_activity_start_time_distributions(self):
        self.__get_activity_data()

        df = self.__activity_data[
            (self.__activity_data["mode"] != "NO_MOVE") | (self.__activity_data["type"] != "HOME")
        ]
        # ~ 1000 trips per bin on average worked well for both Bloomington and Austin
        bins = int(max(30, np.floor(df.shape[0] / 1000)))
        y, x = np.histogram(df.start_time.to_numpy(), bins=bins)
        return pd.DataFrame({"activity_start": x[1:], "activities": y})

    def __get_trip_data(self):
        if self.__trip_data.shape[0] > 0:
            return
        _ = ScenarioCompression.maybe_extract(self.inputs.supply_db)
        _ = ScenarioCompression.maybe_extract(self.inputs.demand_db)

    @kpi_type((KPITag.TRIPS, KPITag.VALIDATION))
    def metric_county_to_county_demand(self):
        # Use ~30 hours to catch any trips that roll over the day border
        sql = """SELECT COALESCE(lo.county, "NON_REPORTED") AS origin_county,
                        COALESCE(ld.county, "NON_REPORTED") AS destination_county,
                        mode AS mode_desc, count(*) AS trips FROM Trip t
                JOIN a.location lo ON t.origin = lo.location
                JOIN a.location ld ON t.destination = ld.location
                WHERE t.mode IN (0, 9, 17, 18, 19, 20)
                  AND t.has_artificial_trip <> 1 and t.start>=0
                  AND t.end<=110000
                  AND t.end > t.start
                  AND t.routed_travel_time > 0
                GROUP BY origin_county, destination_county, mode_desc"""

        return self._slow_fast(sql, "county_to_county_trips", attach_db_type=DatabaseType.Supply)

    def __get_activity_data(self):
        if self.__activity_data.shape[0] > 0:
            return
        _ = ScenarioCompression.maybe_extract(self.inputs.supply_db)
        _ = ScenarioCompression.maybe_extract(self.inputs.demand_db)

        am = ActivityMetrics(supply_file=self.inputs.supply_db, demand_file=self.inputs.demand_db)
        self.__activity_data = am.data

    @kpi_type(KPITag.POPULATION)
    def metric_average_vehicle_ownership(self):
        """This metric retrieves the average household vehicle ownership from the synthetic population in the output"""
        sql_slow = """SELECT avg(vehicles) as avg_hh_veh_from_hh, sum(vehicles) as tot_hh_veh_from_hh,
                        avg(case when num_vehicle_records is null then 0 else num_vehicle_records end) as avg_hh_veh_from_veh,
                        sum(case when num_vehicle_records is null then 0 else num_vehicle_records end) as tot_hh_veh_from_veh FROM
                        (Select * from Household h LEFT JOIN (SELECT hhold, count(*) as num_vehicle_records FROM Vehicle v GROUP by 1) v
                        ON h.household = v.hhold);
                    """
        return self._slow_fast(sql_slow, "average_vehicle_ownership", attach_db_type=DatabaseType.Demand)

    @kpi_type((KPITag.CONVERGENCE, KPITag.HIGH_MEMORY, KPITag.HIGH_CPU, KPITag.BROKEN))
    def metric_traffic_cumulative_gap(self):
        """This metric is slow, memory heavy, broken after hdf5 migration and not used very often. Renaming it to
        m_etric to remove it from auto-running.
        """
        self.__get_path_data()
        metrics = {
            "value_Switch_Cause": "By switch cause",
            "value_Number_of_Switches": "By number of switches",
            "has_artificial_trip": "By artificial trip",
            "mode_desc": "Traffic mode",
        }

        df = self.__path_data.rename(columns={"mend": "Trip end minute"})
        all_metrics = []
        for metric, label in metrics.items():
            if metric not in df.columns:
                logging.info(f"Metric: {metric} not available")
                continue
            data = df.groupby([metric, "Trip end minute"]).sum()[["absolute_gap"]].reset_index()

            pvt = data.pivot_table(index="Trip end minute", values="absolute_gap", columns=metric, fill_value=0)
            pvt = pvt.reset_index()
            output = pd.DataFrame({"Trip end minute": pvt["Trip end minute"]})
            for c in data[metric].unique():
                output[f"{c}"] = pvt[c].cumsum()
            output["metric"] = label
            all_metrics.append(output)
        return pd.concat(all_metrics)

    def __get_path_data(self):
        if self.__path_data.shape[0] > 0:
            return
        _ = ScenarioCompression.maybe_extract(self.inputs.demand_db)

        pm = PathMetrics(demand_file=self.inputs.demand_db, h5_file=self.inputs.result_h5)
        self.__path_data = pm.data
