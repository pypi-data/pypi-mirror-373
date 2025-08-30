# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import warnings
from pathlib import Path
from typing import List

import pandas as pd

from polaris.runs.results.h5_results import H5_Results
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.db_utils import commit_and_close, has_table


class PathMetrics:
    """Loads all data required for the computation of metrics on Paths."""

    def __init__(self, demand_file: Path, h5_file: Path):
        """
        :param demand_file: Path to the result file we want to compute metrics for
        """
        self.__demand_file = ScenarioCompression.maybe_extract(demand_file)
        self.__result_h5 = h5_file
        self.__start = 0
        self.__end = 24
        self.__data = pd.DataFrame([])
        self.__all_modes: List[str] = []
        self.__all_types: List[str] = []

    @property
    def data(self) -> pd.DataFrame:
        if self.__data.empty:
            dt = self.__get_data()

            dt.loc[dt.has_artificial_trip == 2, "absolute_gap"] = 2 * dt.routed_travel_time
            dt.loc[dt.has_artificial_trip.isin([0, 3, 4]), "absolute_gap"] = abs(dt.travel_time - dt.routed_travel_time)

            dt.loc[dt.absolute_gap < 0, "absolute_gap"] = 0
            self.__data = dt.assign(mstart=(dt.tstart / 60).astype(int), mend=(dt.tend / 60).astype(int))
        return self.__data

    def __get_data(self):
        # TODO: Remove support for Path_Links SQLite table before the 2025-03 release
        with commit_and_close(self.__demand_file) as conn:
            if has_table(conn, "Path_Links"):
                deprecation_warning = "Path_Links no longer exists in the demand DB. Its support will be phased out"
                warnings.warn(deprecation_warning, DeprecationWarning, stacklevel=2)
                sql = """SELECT
                                pl.object_id,
                                pl.value_link,
                                pl.value_travel_time travel_time,
                                pl.value_routed_travel_time routed_travel_time,
                                pl.value_Number_of_Switches,
                                pl.value_Switch_Cause,
                                t.has_artificial_trip,
                                t.start tstart,
                                t.end tend,
                                t.mode mode_desc
                                FROM Path_links pl
                                INNER JOIN
                                Trip t
                                ON pl.object_id=t.path
                                WHERE (t.mode = 0 or t.mode = 9 or t.mode = 17 or t.mode = 18 or t.mode = 19 or t.mode = 20)
                                AND t.has_artificial_trip <> 1
                                AND t.end > t.start
                                AND t.routed_travel_time > 0
                                AND pl.value_travel_time>0;
                                """
                return pd.read_sql(sql, conn)
            trip_sql = """SELECT
                                 path path_id,
                                 has_artificial_trip,
                                 "start" tstart,
                                 "end" tend,
                                 "mode" mode_desc
                                 FROM Trip
                                 WHERE Trip.mode in (0, 9, 17, 18, 19, 20)
                                 AND has_artificial_trip <> 1
                                 AND Trip.end > Trip.start
                                 AND routed_travel_time > 0;
                                """
            trips = pd.read_sql(trip_sql, conn)
        df = H5_Results(self.__result_h5).get_path_links().query("travel_time > 0")
        return df.merge(trips, on="path_id", how="right")
