# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import hashlib
import warnings
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from polaris.network.constants import constants
from polaris.network.utils.srid import get_srid
from polaris.network.tools.geo import Geo
from polaris.network.transit.transit_elements.link import Link
from polaris.network.transit.transit_elements.mode_correspondence import mode_correspondence
from polaris.network.transit.transit_elements.pattern import Pattern
from polaris.network.transit.transit_elements.route import Route
from polaris.network.transit.transit_elements.stop import Stop
from polaris.network.transit.transit_elements.trip import Trip
from polaris.utils.database.db_utils import commit_and_close, read_and_close
from shapely import LineString, Point, MultiLineString
from .functions.del_pattern import delete_pattern
from .functions.del_trip import delete_trip


class EditSupply:
    def __init__(self, default_capacities, path_to_file):
        self.default_capacities = default_capacities
        self.path_to_file = path_to_file
        self.geotool = Geo(path_to_file)
        c = constants()
        c.initialize(path_to_file)
        self.__data_cache = {}

    def set_capacity_by_route_type(self, route_type: int, seated: int, total: int, design=None):
        """Sets vehicle capacities for routes with a certain route type/mode

        Args:
            *route_type* (:obj:`int`): Route mode as defined in GTFS (e.g. Bus=3)

            *seated* (:obj:`int`): Number of seated passengers possible

            *total* (:obj:`int`): Number of TOTAL passengers possible

            *design* (:obj:`int`, *Optional*): Number of passengers possible by design. Defaults to total
        """
        design = design or total
        with commit_and_close(self.path_to_file, spatial=True) as conn:
            sql = """UPDATE  Transit_Routes  set seated_capacity=?, design_capacity=?, total_capacity=?
                     WHERE "type"=?"""
            conn.execute(sql, [seated, design, total, route_type])

    def set_capacity_by_route_id(self, route: str, seated: int, total: int, design=None, number_of_cars=0):
        """Sets vehicle capacities for an specific route_id

        Args:
            *route* (:obj:`str`): Route_id as present in the GTFS databasez

            *seated* (:obj:`int`): Number of seated passengers possible

            *total* (:obj:`int`): Number of TOTAL passengers possible

            *design* (:obj:`int`, *Optional*): Number of passengers possible by design. Defaults to total

            *number_of_cars* (:obj:`int`, *Optional*): Number of cars operating the route (applies to trains)
        """
        with commit_and_close(self.path_to_file, spatial=True) as conn:
            if design is None:
                design = total
            sql = """UPDATE  Transit_Routes  set seated_capacity=?, design_capacity=?, total_capacity=?,
                                                 number_of_cars=? where "route_id"=?"""
            conn.execute(sql, [seated, design, total, number_of_cars, route])

    def delete_route(self, route_id: int):
        """Deletes all information regarding one specific route

        Args:
            *route_id* (:obj:`str`): Route_id as present in the database
        """
        with commit_and_close(self.path_to_file, spatial=True) as conn:
            sql = "SELECT pattern_id from Transit_Patterns where route_id=?"
            patterns = [x[0] for x in conn.execute(sql, [route_id])]
            for pat in patterns:
                delete_pattern(pat, conn)

    def delete_pattern(self, pattern_id: int):
        """Deletes all information regarding one specific transit_pattern

        Args:
            *pattern_id* (:obj:`str`): pattern_id as present in the database
        """
        with commit_and_close(self.path_to_file, spatial=True) as conn:
            delete_pattern(pattern_id, conn)

    def add_stop(
        self, agency_id: int, route_type: int, stop_code: str, latitude: float, longitude: float, **kwargs
    ) -> int:
        """ """
        with commit_and_close(self.path_to_file, spatial=True) as conn:
            sql = "SELECT count(*) from Transit_Stops where stop=?"
            if conn.execute(sql, [stop_code]).fetchone()[0] > 0:
                raise ValueError("Another stop with this name/code already exists. Can't add another one")
            sql = "SELECT count(*) from Transit_Stops where x=? and y=?"
            if conn.execute(sql, [round(longitude, 8), round(latitude, 8)]).fetchone()[0] > 0:
                raise ValueError("Another stop already exists in that coordinate. Cannot add another one")

            stp = Stop(agency_id=agency_id)
            if kwargs:
                stp.populate(tuple(kwargs.values()), list(kwargs.keys()))
            stp.stop_lon = longitude
            stp.stop_lat = latitude
            stp.get_node_id()
            stp.stop = stop_code
            stp.route_type = route_type
            stp.geo = Point(longitude, latitude)

            stp.srid = get_srid(conn=conn)
            stp.save_to_database(conn, commit=True)
        return stp.stop_id

    def add_route(self, agency_id: int, mode_id: int, route_name: str, shape: Optional[MultiLineString] = None) -> int:
        """ """
        with commit_and_close(self.path_to_file, spatial=True) as conn:
            sql = "SELECT count(*) from Transit_Agencies where agency_id=?"
            if conn.execute(sql, [agency_id]).fetchone()[0] == 0:
                raise ValueError("Agency ID does not exist. Route cannot be added")

            sql = "SELECT count(*) from Transit_Routes where shortname=? or longname=? or route=?"
            if conn.execute(sql, [route_name, route_name, route_name]).fetchone()[0] > 0:
                raise ValueError(f"There is already a route with name {route_name}. Route cannot be added")

            rt = Route(agency_id)
            rt.get_route_id()
            rt.route = rt.route_id
            rt.route_type = mode_id
            rt.route_long_name = rt.route_short_name = route_name
            rt.shape = shape
            rt.srid = get_srid(conn=conn)
            caps = self.default_capacities.get(mode_id, [0, 0, 0])
            rt.seated_capacity, rt.design_capacity, rt.total_capacity = caps
            rt.save_to_database(conn=conn, commit=True)
        return rt.route_id

    def add_route_pattern(self, route_id: int, stop_sequence: List[int], shape: Optional[LineString] = None) -> int:
        """ """

        with commit_and_close(self.path_to_file, spatial=True) as conn:
            rt = conn.execute("""SELECT "type" from Transit_Routes where route_id=?""", [route_id]).fetchone()
            if rt is None:
                raise ValueError("Route ID does not exist in the database")
            rt = Route(-1).from_database(conn, route_id)
            rt.srid = get_srid(conn=conn)

            list_stops = [Stop(-1).from_database(conn, stop_id) for stop_id in stop_sequence]

            p = Pattern(self.geotool, route_id, None, path_to_file=self.path_to_file)

            m = hashlib.md5()
            m.update(str(route_id).encode())
            m.update("".join([str(stp) for stp in stop_sequence]).encode())
            p.pattern_hash = m.hexdigest()

            p.route = str(route_id)
            p.route_type = int(rt.route_type)
            p.raw_shape = shape
            p.get_pattern_id()
            p.stops = list_stops

            p.links.clear()
            prev_end = list_stops[0].geo
            for i in range(1, len(list_stops)):
                link = Link(rt.srid)
                link.pattern_id = p.pattern_id
                link.get_link_id()
                fnode = list_stops[i - 1].stop_id
                tnode = list_stops[i].stop_id
                link.from_node = fnode
                link.to_node = tnode
                link.build_geo(list_stops[i - 1].geo, list_stops[i].geo, None, prev_end)
                prev_end = list_stops[i].geo
                link.type = int(p.route_type)
                link.save_to_database(conn=conn, commit=True)
                p.links.append(link.transit_link)

            if rt.route_type in mode_correspondence.keys():
                p.map_match()
            else:
                warnings.warn(f"Polaris does not support map-matching routes with type {rt.route_type}")
            p.save_to_database(conn, commit=True)
        return p.pattern_id

    def add_pt_trip(
        self,
        pattern_id: int,
        departure_time: int,
        default_speed,
        force_default_speed=False,
        speed_factor=1.0,
        horizon_begin=0.0,
        horizon_end=86400.0,
        **kwargs,
    ) -> int:
        """Adds one trip for a given pattern ID

        Args:
            *pattern_id* (:obj:`int`): ID of the route pattern for which to add a route

            *departure_time* (:obj:`int`): departure time for the trip in SECONDS

            *default_speed* (:obj:`float`): Speed for the trip in case one cannot be derived from existing trips

            *force_default_speed* (:obj:`Bool`, *Optional*): Uses the parameter *default_speed* regardless of data
            being found on the database

            *speed_factor* (:obj:`float`, *Optional*): Multiplier of the speed found in the database. Defaults to 1.0,
            and does NOT apply to the *default_speed* parameter provided by the user

            *horizon_begin* (:obj:`int`, *Optional*): Beginning of the interval in which to search for data for computing
            speeds for the new trip. Applies to the **start** of the trips. Between 0 and 86399

            *horizon_end* (:obj:`int`, *Optional*): End of the interval in which to search for data for computing
            speeds for the new trip. Applies to the **start** of the trips. Between 1 and 86400

            *kwargs* (*Optional*): Any characteristics to append to the trip (e.g. vehicle capacity)
        """
        self.__cache_data()
        with commit_and_close(self.path_to_file, spatial=True) as conn:
            df = self.__data_cache["route_types"]
            df = df[df.pattern_id == pattern_id]
            if df.empty:
                raise ValueError("Pattern ID does not exist")
            r_id = df.route_id.values[0]
            arrivals, departures, source_time = self.__get_trip_interv(
                r_id,
                pattern_id,
                departure_time,
                default_speed,
                force_default_speed,
                speed_factor,
                horizon_begin,
                horizon_end,
                conn,
            )

            trip = self.__create_add_trip(arrivals, conn, departures, kwargs, pattern_id, source_time)
            return trip.trip_id

    def ensure_pattern_departures(
        self,
        pattern_id: int,
        departure_times: List[int],
        default_speed: float,
        force_default_speed=False,
        speed_factor=1.0,
        horizon_begin=0.0,
        horizon_end=86400.0,
        **kwargs,
    ) -> Tuple[List, List]:
        """Ensures that the trips for a given pattern within a certain interval follow an exact list of departure times

        Args:
            *pattern_id* (:obj:`int`): ID of the route pattern for which to add a route

            *departure_times* (:obj:`List`): List of all the departure times that should exist for this interval

            *default_speed* (:obj:`float`): Speed for the trip in case one cannot be derived from existing trips

            *force_default_speed* (:obj:`Bool`, *Optional*): Uses the parameter *default_speed* regardless of data
            being found on the database

            *speed_factor* (:obj:`float`, *Optional*): Multiplier of the speed found in the database. Defaults to 1.0,
            and does NOT apply to the *default_speed* parameter provided by the user

            *horizon_begin* (:obj:`int`, *Optional*): Beginning of the interval in which to search for data for computing
            speeds for the new trip. Applies to the **start** of the trips. Between 0 and 86399

            *horizon_end* (:obj:`int`, *Optional*): End of the interval in which to search for data for computing
            speeds for the new trip. Applies to the **start** of the trips. Between 1 and 86400

            *kwargs* (*Optional*): Any characteristics to append to the trip (e.g. vehicle capacity)
        """
        self.__cache_data()

        # First select the trips that should delete after we are done
        all_trips = self.__data_cache["transit_trips"][self.__data_cache["transit_trips"].pattern_id == pattern_id]
        delete_trips, added_trips = [], []
        if not all_trips.empty:
            departures = self.__data_cache["trip_departures"]
            to_delete = departures[departures.trip_id.isin(all_trips.trip_id)]
            to_delete = to_delete[(to_delete.inst >= horizon_begin) & (to_delete.inst <= horizon_end)]
            delete_trips = to_delete.trip_id.tolist()

        with commit_and_close(self.path_to_file, spatial=True) as conn:
            df = self.__data_cache["route_types"]
            df = df[df.pattern_id == pattern_id]
            if df.empty:
                raise ValueError("Pattern ID does not exist")

            r_id = df.route_id.values[0]

            # Second, we first compute the departure times for one of the the departures
            arr, deps, source_time = self.__get_trip_interv(
                r_id,
                pattern_id,
                0,
                default_speed,
                force_default_speed,
                speed_factor,
                horizon_begin,
                horizon_end,
                conn,
            )

            # Third, we iterate over all departure times and add the trips
            for departure_time in departure_times:
                arrivals = (np.array(arr) + departure_time).astype(int)  # type: np.ndarray
                departures = (np.array(deps) + departure_time).astype(int)
                trip = self.__create_add_trip(arrivals, conn, departures, kwargs, pattern_id, source_time)
                added_trips.append(trip.trip_id)

            for trip_id in delete_trips:
                delete_trip(trip_id, conn, False)

        return added_trips, delete_trips

    def suggest_departures(self, intervals: dict) -> List[int]:
        """It builds a list of suggested trip departures based on a list of intervals and headways.
        The format of the inputs is the following:

            intervals = [
                         {"start": 0, "end": 3600, "headway": 1400},
                         {"start": 3600, "end": 7200, "headway": 1200},
                         {"start": 7200, "end": 10800, "headway": 1000},
                         {"start": 14400, "end": 18000, "headway": 1200},
                        ]
        """

        # Algorithm suggested and implemented by Omer Verbas: 18/Jul/2023

        trip_starts = []
        instant = -1
        former_headway = -1
        former_end = -1
        for interv in intervals:
            if interv["start"] == former_end:
                shift = (interv["headway"] + former_headway) / 2
            else:
                shift = interv["headway"] / 2
                instant = interv["start"]

            instant += shift
            trip_starts.append(instant)
            while instant + interv["headway"] <= interv["end"]:
                instant += interv["headway"]
                trip_starts.append(instant)
            former_headway = interv["headway"]
            former_end = interv["end"]
        return trip_starts

    def clear_data_cache(self):
        self.__data_cache.clear()

    def __cache_data(self):
        if self.__data_cache:
            return
        warnings.warn("Caching data")
        sql1 = """SELECT pattern_id, sum("length") dist FROM Transit_Links GROUP BY pattern_id"""
        sql2 = """SELECT tt.pattern_id, tts.trip_id, max(tts.arrival)-min(tts.arrival) duration
                   FROM Transit_Trips_Schedule tts
                   INNER JOIN Transit_Trips tt ON tts.trip_id=tt.trip_id GROUP BY pattern_id, tts.trip_id"""
        sql3 = """SELECT tp.pattern_id, tp.route_id, tr.type route_type
                  FROM Transit_Patterns tp
                  INNER JOIN Transit_Routes tr ON tp.route_id=tr.route_id"""
        sql4 = """SELECT trip_id, arrival % 86400 inst from Transit_Trips_Schedule where "index"=0"""
        sql5 = "SELECT * from Transit_Links"
        sql6 = """SELECT tt.pattern_id, tts."index" idx, tts.arrival, tts.departure, tts.arrival % 86400 inst, tts.trip_id FROM Transit_Trips_Schedule tts
                  INNER JOIN Transit_Trips tt ON tts.trip_id=tt.trip_id"""
        sql7 = "SELECT pattern_id, trip_id FROM Transit_Trips"
        with read_and_close(self.path_to_file, spatial=True) as conn:
            self.__data_cache["distances"] = pd.read_sql(sql1, conn)
            self.__data_cache["durations"] = pd.read_sql(sql2, conn)
            self.__data_cache["route_types"] = pd.read_sql(sql3, conn)
            self.__data_cache["trip_departures"] = pd.read_sql(sql4, conn)
            self.__data_cache["pattern_links"] = pd.read_sql(sql5, conn)
            self.__data_cache["trip_schedule"] = pd.read_sql(sql6, conn)
            self.__data_cache["transit_trips"] = pd.read_sql(sql7, conn)

    def __get_trip_interv(
        self,
        route_id,
        pattern_id,
        departure_time,
        default_speed,
        force_default_speed,
        speed_factor,
        horizon_begin,
        horizon_end,
        conn,
    ):
        route = Route(-1).from_database(conn, route_id)
        links = self.__data_cache["pattern_links"]
        links = links[links.pattern_id == pattern_id]
        if links.empty:
            raise ValueError("The pattern exists, but no links are present in the database")

        # We try to get the info from trips for the same pattern
        trips = self.__data_cache["transit_trips"][self.__data_cache["transit_trips"].pattern_id == pattern_id]
        if trips.shape[0] > 0 and not force_default_speed:
            sch = self.__data_cache["trip_schedule"]
            sch = sch[sch.trip_id.isin(trips.trip_id.tolist())]

            # Makes sure we get the trips that wrap around the day as well.
            # Maybe we should just set the trips to start on the same day (arrival-86400) for all trips that start
            # after 86400 on GTFS import
            data = sch[(sch.idx == 0) & (sch.inst % 86400 >= horizon_begin) & (sch.inst % 86400 <= horizon_end)]
            interest = data.trip_id.unique().tolist()

            dt = sch[sch.trip_id.isin(interest)]
            if dt.empty:
                dt = sch
                warnings.warn(
                    f"Could not find trips within the requested interval: {horizon_begin} - {horizon_end}. Using the entire day"
                )

            avg_tm = dt.groupby(["idx"]).mean()[["arrival", "departure"]].reset_index()
            avg_tm.sort_values(by=["idx"], inplace=True)
            avg_tm.loc[:, "arrival"] = departure_time + (avg_tm.arrival - avg_tm.arrival.min()) / speed_factor
            avg_tm.loc[:, "departure"] = departure_time + (avg_tm.departure - avg_tm.departure.min()) / speed_factor
            arrivals = avg_tm.arrival.astype(int).tolist()
            departures = avg_tm.departure.astype(int).tolist()
            source_time = [3] * len(arrivals)
        else:
            distances = self.__data_cache["distances"]
            durations = self.__data_cache["durations"]
            route_types = self.__data_cache["route_types"]
            tst = self.__data_cache["trip_departures"]

            # Same thing. Makes thing we wrap around the day
            data = tst[(tst.inst % 86400 >= horizon_begin) & (tst.inst % 86400 <= horizon_end)]
            trips_of_interest = data.trip_id.unique().tolist()

            durations = durations[durations.trip_id.isin(trips_of_interest)]
            if not durations.empty:
                durations = durations[["pattern_id", "duration"]].groupby(["pattern_id"]).mean().reset_index()

            speed_to_use = default_speed
            if not force_default_speed and min(distances.shape[0], durations.shape[0], route_types.shape[0]) > 0:
                distances = distances.merge(route_types, on="pattern_id", how="left")
                speeds = distances.merge(durations, on="pattern_id")
                speeds = speeds.assign(speed=speeds.dist / speeds.duration)

                # We compute the average speed for increasing levels of relevance (route type, route id, pattern id)
                # to get the most relevant route speed possible

                # Get the speed by route type
                abs_speeds = speeds[["route_type", "speed"]].groupby(["route_type"]).mean().reset_index()
                tp_speeds = abs_speeds[abs_speeds.route_type == route.route_type]
                if not tp_speeds.empty:
                    speed_to_use = tp_speeds.speed.tolist()[0]

                # Get the speed by route_id
                abs_speeds = speeds[["route_id", "speed"]].groupby(["route_id"]).mean().reset_index()
                tp_speeds = abs_speeds[abs_speeds.route_id == route.route_id]
                if not tp_speeds.empty:
                    speed_to_use = tp_speeds.speed.tolist()[0]

                # Get the speed by route_id
                abs_speeds = speeds[["pattern_id", "speed"]].groupby(["pattern_id"]).mean().reset_index()
                tp_speeds = abs_speeds[abs_speeds.pattern_id == pattern_id]
                if not tp_speeds.empty:
                    speed_to_use = tp_speeds.speed.tolist()[0]
                speed_to_use *= speed_factor

            arr = [int(x) for x in [departure_time] + list(links["length"].values / speed_to_use)]
            arrivals = list(np.cumsum(arr).astype(int))
            departures = arrivals
            source_time = [4] * len(arrivals)

        return arrivals, departures, source_time

    def __create_add_trip(self, arrivals, conn, departures, kwargs, pattern_id, source_time):
        trip = Trip()
        trip.pattern_id = pattern_id
        trip.arrivals = arrivals
        trip.departures = departures
        trip.source_time = source_time
        if kwargs:
            trip._populate(tuple(kwargs.values()), list(kwargs.keys()))
        trip.get_trip_id()
        trip.save_to_database(conn, False)
        return trip
