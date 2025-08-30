# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import warnings
from pathlib import Path
from typing import List

import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.runs.results.h5_results import H5_Results
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.db_utils import read_sql, read_and_close, has_table, commit_and_close


class TNCMetrics:
    """Loads all data required for the computation of TNC metrics and
    creates permanent tables with statistics in the demand database.

    The behavior of time filtering consists of setting to instant zero
    whenever *from_time* is not provided and the end of simulation when
    *to_time* is not provided"""

    def __init__(self, supply_file: Path, demand_file: Path, result_file: Path, result_h5: Path):
        """
        :param supply_file: Path to the supply file
        :param demand_file: Path to the demand file we want to compute metrics for
        :param result_file: Path to the result file
        :param result_h5: Path to the result h5 file
        """

        self.__loc_data = pd.DataFrame([])
        self.__link_data = pd.DataFrame([])
        self.__demand_file = ScenarioCompression.maybe_extract(demand_file)
        self.__supply_file = supply_file
        self.__result_file = result_file
        self.__result_h5 = result_h5

        self.tables: List[str] = []
        self.__wait_times_base_data = pd.DataFrame([])
        self.__revenue_base_data = pd.DataFrame([])
        self.__tnc_initial_loc = pd.DataFrame([])
        self.__vmt_by_link = pd.DataFrame([])
        self.__failed_requests = pd.DataFrame([])

        self.__list_tables()
        self.__get_supply_data()

    @staticmethod
    def list_zone_metrics() -> list:
        """Returns list of metrics available for traffic analysis zones"""
        return ["mean_wait", "initial_locations", "failed_requests", "revenue"]

    @staticmethod
    def list_link_metrics() -> list:
        """Returns list of metrics available for traffic analysis zones"""
        return ["link_use"]

    @staticmethod
    def list_location_metrics() -> list:
        """Returns list of metrics available for traffic analysis zones"""
        return ["mean_wait", "initial_locations", "failed_requests", "revenue"]

    def wait_metrics(self, from_minute=None, to_minute=None, aggregation="zone") -> pd.DataFrame:
        """
        Computes wait times within each zone or at each location. Allows constraining to a given
        time interval.

            All parameters are optional.

        :param from_minute: Start of the interval for computation. Zero if not provided
        :param to_minute: End of the interval for computation. Maximum time from the dataset if not provided
        :param aggregation: Determine aggregation level. Zone if not provided.
        :return: Statistics DataFrame
        """
        self.__create_wait_tables()

        fm = 0 if from_minute is None else from_minute
        tm = self.__wait_times_base_data.to_minute.max() if to_minute is None else to_minute

        filtered_wait_data = self.__wait_times_base_data.loc[self.__wait_times_base_data.from_minute >= fm, :]
        filtered_wait_data = filtered_wait_data.loc[filtered_wait_data.to_minute <= tm, :]

        if aggregation == "zone":
            gpb = filtered_wait_data.merge(self.__loc_data, on="location", how="left")
            groupby = gpb.groupby(["zone"])
        elif aggregation == "location":
            groupby = filtered_wait_data.groupby(["location"])
        else:
            raise ValueError("Aggregation of wait times needs to be done by zone or location only")

        means = groupby.mean()[["mean_wait"]]

        return means.fillna(0)

    def revenue_metrics(self, from_minute=None, to_minute=None, aggregation="zone", agg_on="origin") -> pd.DataFrame:
        """
        Computes TNC revenue within each zone. Allows constraining to a given
        time interval in hours.

            All parameters are optional.

        :param from_minute: Start of the interval for computation. Zero if not provided
        :param to_minute: End of the interval for computation. Maximum time from the dataset if not provided
        :param aggregation: Aggregation level allowed. "zone" or "location". Defaults to "zone"
        :param agg_on: on which trip end aggreation should be done: "origin" or "destination". Defaults to "origin"
        :return: Statistics DataFrame
        """

        self.__create_revenue_tables()

        fm = 0 if from_minute is None else from_minute
        tm = self.__revenue_base_data.to_minute.max() if to_minute is None else to_minute

        df = self.__revenue_base_data.loc[self.__revenue_base_data.from_minute >= fm, :]
        df = df.loc[df.to_minute <= tm, :]
        df.rename(columns={agg_on: "location"}, inplace=True)
        if aggregation == "zone":
            df = df.merge(self.__loc_data, on="location", how="left")

        return df.groupby([aggregation]).sum()[["revenue"]]

    def initial_loc_metrics(self, aggregation="location", **kwargs) -> pd.DataFrame:
        """
        Displays TNC initial locations aggregated by location or zone. Vehicles with human and automated
        drivers are computed separately

            All parameters are optional.

        :param aggregation: Filter to see either only human drivers or AVs. No filter if not provided
        :return: Statistics DataFrame
        """
        self.__create_tnc_initial_location_tables()

        df = self.__tnc_initial_loc

        gpb = pd.DataFrame(df.groupby([aggregation, "driver"]).size())
        gpb.columns = ["vehicles"]  # type: ignore # Recommended Pandas behaviour that should not trigger typing
        gpb = gpb.unstack(level=-1)  # type: ignore # Some Pandas issue
        gpb.columns = gpb.columns.droplevel(0)
        gpb.index.name = aggregation

        for f in ["human", "automated"]:
            if f not in gpb.columns:
                gpb[f] = 0
        gpb = gpb.assign(all_vehicles=0)
        gpb["all_vehicles"] = gpb.sum(axis=1)
        return gpb.fillna(0)

    def link_use(self, from_minute=None, to_minute=None, unit="mile") -> pd.DataFrame:
        """
        Computes TNC VMT by link. Can be optionally constrained to a time window.

            All parameters are optional.

        :param from_minute: Start of the interval for computation. Zero if not provided
        :param to_minute: End of the interval for computation. Maximum time from the dataset if not provided
        :param unit: Unit of the metric. Available units are: 'km' and 'mile' (default)
        :return: Statistics DataFrame
        """

        self.__create_link_use_tables()

        fm = 0 if from_minute is None else from_minute
        tm = self.__vmt_by_link.to_minute.max() if to_minute is None else to_minute

        filtered_vmt_data = self.__vmt_by_link.loc[self.__vmt_by_link.from_minute >= fm, :]
        filtered_vmt_data = filtered_vmt_data.loc[filtered_vmt_data.to_minute <= tm, :]

        gpb = filtered_vmt_data.groupby(["link"]).sum()[["length"]]

        if unit.lower() == "mile":
            gpb.loc[:, "length"] /= 1609.344
            return gpb.rename(columns={"length": "vmt"})
        elif unit.lower() == "km":
            gpb.loc[:, "length"] /= 1000
            return gpb.rename(columns={"length": "vkt"})
        else:
            raise ValueError('Units available are "mile" and "km"')

    def failed_requests(self, from_minute=None, to_minute=None, aggregation="location") -> pd.DataFrame:
        """
        Displays failed TNC requests by zone, location or link defined by parameter.

            All parameters are optional.

        :param from_minute: Start of the interval for computation. Zero if not provided
        :param to_minute: End of the interval for computation. Maximum time from the dataset if not provided
        :param aggregation: Aggregation level of failed requests at 'link', 'location' or 'zone'. Defaults to 'location'
        :return: Statistics DataFrame
        """

        self.__create_failed_requests_table()

        fm = 0 if from_minute is None else from_minute
        tm = self.__failed_requests.request_minute.max() if to_minute is None else to_minute

        filtered_data = self.__failed_requests.loc[self.__failed_requests.request_minute >= fm, :]
        filtered_data = filtered_data.loc[filtered_data.request_minute <= tm, :]

        gpb = pd.DataFrame(filtered_data.groupby([aggregation.lower()]).size())
        gpb.columns = pd.Index(["failed_requests"])

        return gpb.fillna(0)

    def __create_failed_requests_table(self):
        if self.__failed_requests.shape[0] > 0:
            return
        sql = """SELECT TNC_request_id as id, request_time/60 as request_minute,
                        origin_location as location, origin_link as link
                 FROM TNC_Request
                 WHERE assigned_vehicle is null"""
        self.__failed_requests = read_sql(sql, self.__demand_file)
        self.__failed_requests = self.__failed_requests.merge(self.__loc_data, on="location", how="left")
        self.__failed_requests = self.__failed_requests.reset_index()
        self.__failed_requests = self.__failed_requests[["location", "request_minute", "link", "zone"]]

    def __create_wait_tables(self):
        if self.__wait_times_base_data.shape[0] > 0:
            return
        sql = """Select request_time/60 as from_minute, end/60 as to_minute,
                        destination as location, (end - request_time)/60 as mean_wait
                 FROM TNC_Trip
                 WHERE final_status = -1"""
        self.__wait_times_base_data = read_sql(sql, self.__demand_file)

    def __create_revenue_tables(self):
        if self.__revenue_base_data.shape[0] > 0:
            return
        sql = """Select start/60 as from_minute, end/60 as to_minute, origin, destination, fare as revenue
                 FROM TNC_Trip
                 WHERE final_status = -2"""
        self.__revenue_base_data = read_sql(sql, self.__demand_file)

    def __create_tnc_initial_location_tables(self):
        if self.__tnc_initial_loc.shape[0] > 0:
            return
        sql = """Select tnc_id, initial_loc as location,
              (case when human_driver=1 then 'human' else 'automated' end) as driver FROM TNC_Statistics"""
        df = read_sql(sql, self.__result_file)
        self.__tnc_initial_loc = df.merge(self.__loc_data[["location", "zone"]], on="location", how="left")

    def __create_link_use_tables(self):
        if self.__vmt_by_link.shape[0] > 0:
            return

        with commit_and_close(self.__demand_file) as conn:
            if has_table(conn, "Path_Links"):
                # TODO: Remove support for Path_Links SQLite table before the 2025-03 release
                deprecation_warning = "Path_Links no longer exists in the demand DB. Its support will be phased out"
                warnings.warn(deprecation_warning, DeprecationWarning, stacklevel=2)
                sql = """SELECT value_entering_time/60 as from_minute,
                                (value_entering_time + value_travel_time)/60 as to_minute,
                                value_link as link FROM Path_links
                         WHERE object_id in (SELECT path FROM TNC_Trip) and value_travel_time > -1"""
                self.__vmt_by_link = pd.read_sql(sql, conn)
            else:
                trips = read_sql("SELECT path FROM TNC_Trip", conn)
                if trips.empty:
                    return
                df = H5_Results(self.__result_h5).get_path_links().query("travel_time > 0")
                df.query("path_id in @trips.path", inplace=True)
                df = df.assign(from_minute=df.entering_time / 60, to_minute=(df.entering_time + df.travel_time) / 60)
                df.rename(columns={"link_id": "link"}, inplace=True)
                self.__vmt_by_link = df[["from_minute", "to_minute", "link"]]

        self.__vmt_by_link = self.__vmt_by_link.merge(self.__link_data, on="link", how="left")

    def __get_supply_data(self):
        data = DataTableAccess(self.__supply_file)
        self.__loc_data = data.get("location")[["location", "zone", "stop_flag"]]
        self.__link_data = data.get("link")[["link", "length"]]

    def __list_tables(self):
        if self.__demand_file is None:
            self.tables.clear()
            return
        with read_and_close(self.__demand_file) as conn:
            self.tables = [x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type ='table'").fetchall()]
