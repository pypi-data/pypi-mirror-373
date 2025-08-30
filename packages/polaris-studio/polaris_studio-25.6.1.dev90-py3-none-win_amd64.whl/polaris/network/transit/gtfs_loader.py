# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import hashlib
import logging
import zipfile
from copy import deepcopy
from os import PathLike
from os.path import splitext, basename
from typing import Dict, List, Any

import numpy as np
import pandas as pd
from polaris.network.transit.transit_elements.agency import Agency
from polaris.network.transit.transit_elements.fare import Fare
from polaris.network.transit.transit_elements.fare_rule import FareRule
from polaris.network.transit.transit_elements.route import Route
from polaris.network.transit.transit_elements.service import Service
from polaris.network.transit.transit_elements.stop import Stop
from polaris.network.transit.transit_elements.trip import Trip
from shapely.geometry import LineString

from polaris.network.constants import AGENCY_MULTIPLIER
from polaris.network.utils.srid import get_srid
from polaris.network.transit.column_order import column_order
from polaris.network.transit.date_tools import to_seconds, create_days_between, format_date
from polaris.network.transit.parse_csv import parse_csv
from polaris.network.utils.worker_thread import WorkerThread
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.optional_deps import check_dependency
from polaris.utils.signals import SIGNAL


class GTFSReader(WorkerThread):
    """Loader for GTFS data. Not meant to be used directly by the user"""

    polaris_logging()
    signal = SIGNAL(object)

    def __init__(self, path_to_file: PathLike):
        WorkerThread.__init__(self, None)
        check_dependency("pyproj")
        import pyproj
        from pyproj import Transformer

        self.__capacities__: Dict[int, List[int]] = {}
        self.__max_speeds__: Dict[int, pd.DataFrame] = {}
        self.feed_date = ""
        self.agency = Agency(path_to_file)
        self.services: Dict[str, Service] = {}
        self.routes: Dict[int, Route] = {}
        self.trips: Dict[int, List[Trip]] = {}
        self.stops: Dict[int, Stop] = {}
        self.stop_times: Dict[str, pd.DataFrame] = {}
        self.shapes: Dict[Any, LineString] = {}
        self.fare_rules: List[FareRule] = []
        self.fare_attributes: Dict[str, Fare] = {}
        self.feed_dates: List[str] = []
        self.data_arrays = {}  # type: Dict[str, np.recarray]
        self.wgs84 = pyproj.Proj("epsg:4326")
        self.srid = get_srid(database_path=path_to_file)
        self.transformer = Transformer.from_crs("epsg:4326", f"epsg:{self.srid}", always_xy=False)
        self.__mt = ""
        self.__path_to_tile = path_to_file
        self._exception_inconsistencies = 0

    def set_feed_path(self, file_path):
        """Sets GTFS feed source to be used
        Args:
            *file_path* (:obj:`str`): Full path to the GTFS feed (e.g. 'D:/project/my_gtfs_feed.zip')
        """

        self.archive_dir = file_path
        self.zip_archive = zipfile.ZipFile(self.archive_dir)
        ret = self.zip_archive.testzip()
        if ret is not None:
            self.__fail(f"GTFS feed {file_path} is not valid")

        self.__load_feed_calendar()
        self.zip_archive.close()

        self.feed_date = splitext(basename(file_path))[0]
        self.__mt = f"Reading GTFS for {self.agency.agency}"

    def _set_capacities(self, capacities: dict):
        self.__capacities__ = capacities

    def _set_maximum_speeds(self, max_speeds: dict):
        self.__max_speeds__ = max_speeds

    def load_data(self, service_date: str):
        ag_id = self.agency.agency
        self.__mt = f"Reading GTFS for {ag_id}"

        logging.info(f"Loading data for {service_date} from the {ag_id} GTFS feed. This may take some time")
        self.signal.emit(["start", "master", 6, self.__mt, self.__mt])

        self.__load_date()

        self.finished()

    def finished(self):
        self.signal.emit(["finished_static_gtfs_procedure"])

    def __load_date(self):
        logging.debug("Starting __load_date")
        self.zip_archive = zipfile.ZipFile(self.archive_dir)
        self.__load_routes_table()

        self.__load_stops_table()

        self.__load_stop_times()

        self.__load_trips_table()

        self.__deconflict_stop_times()

        self.__load_shapes_table()

        self.__load_fare_data()

        self.zip_archive.close()

    def __deconflict_stop_times(self) -> None:
        logging.info("Starting deconflict_stop_times")

        # loop over all routes and trips
        msg_txt = f"Interpolating stop times for {self.agency.agency}"
        self.signal.emit(["start", "secondary", len(self.trips), msg_txt, self.__mt])
        total_fast = 0
        for prog_counter, route in enumerate(self.trips):
            self.signal.emit(["update", "secondary", prog_counter + 1, msg_txt, self.__mt])
            max_speeds = self.__max_speeds__.get(self.routes[route].route_type, pd.DataFrame([]))
            for trip in self.trips[route]:  # type: Trip
                logging.debug(f"De-conflicting stops for route/trip {route}/{trip.trip}")
                stop_times = self.stop_times[trip.trip]
                if stop_times.shape[0] != len(trip.stops):
                    logging.error(f"Trip {trip.trip_id} has a different number of stop_times than actual stops.")

                if not stop_times.arrival_time.is_monotonic_increasing:
                    stop_times.loc[stop_times.arrival_time == 0, "arrival_time"] = np.nan
                    stop_times.arrival_time = stop_times.arrival_time.ffill()
                diffs = np.diff(np.array(stop_times.arrival_time.to_numpy()))

                stop_geos = [self.stops[x].geo for x in trip.stops]
                distances = np.array([x.distance(y) for x, y in zip(stop_geos[:-1], stop_geos[1:])])

                times = np.array(stop_times.arrival_time.values, copy=True)
                source_time = np.zeros(stop_times.shape[0])

                if times[-1] == times[-2]:
                    logging.debug("    Had conflicting stop times in its end")
                    # We shift the last stop by one second if the stop time is equal to the previous stop
                    times[-1] += 1
                    source_time[-1] = 1
                    diffs = np.diff(times)

                to_override = np.argwhere(diffs == 0)[:, 0] + 1
                if to_override.shape[0] > 0:
                    logging.debug("     Had consecutive stops with the same timestamp")
                    for i in to_override:
                        source_time[i] = 1
                        times[i:] += 1
                    diffs = np.diff(times)

                if max_speeds.shape[0] > 0:
                    speeds = distances / diffs
                    df = pd.DataFrame(
                        {
                            "speed": speeds,
                            "max_speed": max_speeds.speed.max(),
                            "dist": distances,
                            "elapsed_time": diffs,
                            "add_time": np.zeros(diffs.shape[0], dtype=int),
                            "source_time": source_time[1:],
                        }
                    )

                    for _, rec in max_speeds.iterrows():
                        df.loc[(df.dist >= rec.min_distance) & ((df.dist < rec.max_distance)), "max_speed"] = rec.speed

                    to_fix = df[df.max_speed < df.speed].index.values
                    if to_fix.shape[0] > 0:
                        logging.debug(f"     Trip {trip.trip} had {to_fix.shape[0]} segments too fast")
                        total_fast += to_fix.shape[0]
                        df.loc[to_fix[0] :, "source_time"] = 2
                        for i in to_fix:
                            df.loc[i:, "add_time"] += (df.elapsed_time[i] * (df.speed[i] / df.max_speed[i] - 1)).astype(
                                int
                            )

                        source_time[1:] = df.source_time[:]
                        times[1:] += df.add_time[:].astype(int)

                assert min(times[1:] - times[:-1]) > 0
                stop_times.arrival_time.values[:] = times[:].astype(int)
                stop_times.departure_time.values[:] = times[:].astype(int)
                stop_times.source_time.values[:] = source_time[:].astype(int)
                trip.arrivals = stop_times.arrival_time.values
                trip.departures = stop_times.departure_time.values

        if total_fast:
            logging.warning(f"There were a total of {total_fast} segments that were too fast and were corrected")

    def __load_fare_data(self):
        logging.debug("Starting __load_fare_data")
        # GTFS Fare Attributes table
        fareatttxt = "fare_attributes.txt"
        self.fare_attributes = {}
        if fareatttxt in self.zip_archive.namelist():
            logging.debug('  Loading "fare_attributes" table')

            with self.zip_archive.open(fareatttxt, "r") as file:
                fareatt = parse_csv(file, column_order[fareatttxt])
            self.data_arrays[fareatttxt] = fareatt

            for line in range(fareatt.shape[0]):
                data = tuple(fareatt[line][list(column_order[fareatttxt].keys())])
                headers = ["fare_id", "price", "currency", "payment_method", "transfer", "transfer_duration"]
                f = Fare(self.agency.agency_id)
                f.populate(data, headers)
                if f.fare in self.fare_attributes:
                    self.__fail(f"Fare ID {f.fare} for {self.agency.agency} is duplicated")
                self.fare_attributes[f.fare] = f

        # GTFS Fare Rules table
        farerltxt = "fare_rules.txt"
        self.fare_rules.clear()
        if farerltxt not in self.zip_archive.namelist():
            return

        logging.debug('  Loading "fare_rules" table')

        with self.zip_archive.open(farerltxt, "r") as file:
            farerl = parse_csv(file, column_order[farerltxt])
        self.data_arrays[farerltxt] = farerl

        corresp = {}
        zone_id = self.agency.agency_id * AGENCY_MULTIPLIER + 1
        for line in range(farerl.shape[0]):
            data = tuple(farerl[line][list(column_order[farerltxt].keys())])
            fr = FareRule()
            fr.populate(data, ["fare", "route", "origin", "destination", "contains"])
            fr.fare_id = self.fare_attributes[fr.fare].fare_id
            if fr.route in self.routes:
                fr.route_id = self.routes[fr.route].route_id
            fr.agency_id = self.agency.agency_id
            for x in [fr.origin, fr.destination]:
                if x not in corresp:
                    corresp[x] = zone_id
                    zone_id += 1
            fr.origin_id = corresp[fr.origin]
            fr.destination_id = corresp[fr.destination] if fr.destination != "" else fr.destination_id
            self.fare_rules.append(fr) if fr.origin != "" else fr.origin_id

    def __load_shapes_table(self):
        logging.debug("Starting __load_shapes_table")

        logging.debug("    Loading route shapes")
        # GTFS Shapes table
        self.shapes.clear()
        shapestxt = "shapes.txt"
        if shapestxt not in self.zip_archive.namelist():
            return

        with self.zip_archive.open(shapestxt, "r") as file:
            shapes = parse_csv(file, column_order[shapestxt])

        if shapes.shape[0] == 0:
            return
        all_shape_ids = np.unique(shapes["shape_id"]).tolist()
        msg_txt = f"Load shapes - {self.agency.agency}"
        self.signal.emit(["start", "secondary", len(all_shape_ids), msg_txt, self.__mt])

        self.data_arrays[shapestxt] = shapes
        lons, lats = self.transformer.transform(shapes[:]["shape_pt_lat"], shapes[:]["shape_pt_lon"])
        shapes[:]["shape_pt_lat"][:] = lats[:]
        shapes[:]["shape_pt_lon"][:] = lons[:]
        for i, shape_id in enumerate(all_shape_ids):
            self.signal.emit(["update", "secondary", i + 1, msg_txt, self.__mt])
            items = shapes[shapes["shape_id"] == shape_id]
            items = items[np.argsort(items["shape_pt_sequence"])]
            shape = LineString(list(zip(items["shape_pt_lon"], items["shape_pt_lat"])))
            self.shapes[shape_id] = shape

    def __load_trips_table(self):
        logging.debug("Starting __load_trips_table")

        trip_replacements = self.__load_frequencies()

        # Read the GTFS Trips table
        logging.debug('    Loading "trips" table')
        tripstxt = "trips.txt"
        with self.zip_archive.open(tripstxt, "r") as file:
            trips_array = parse_csv(file, column_order[tripstxt])
        self.data_arrays[tripstxt] = trips_array

        msg_txt = f"Load trips - {self.agency.agency}"
        self.signal.emit(["start", "secondary", trips_array.shape[0], msg_txt, self.__mt])
        #           We need to do several consistency checks for this table
        # If trip IDs are unique
        if np.unique(trips_array["trip_id"]).shape[0] < trips_array.shape[0]:
            self.__fail("There are repeated trip IDs in trips.txt")

        # If there are stop times for every single trip
        stp_tm = self.data_arrays["stop_times.txt"]
        diff = np.setdiff1d(trips_array["trip_id"], stp_tm["trip_id"], assume_unique=False)
        if diff.shape[0] > 0:
            diff = ",".join([str(x) for x in diff.tolist()])
            self.__fail(f"There are IDs in trips.txt without any stop on stop_times.txt -> {diff}")

        # If all service IDs are defined in the calendar
        incal = np.unique(list(self.services.keys()))
        diff = np.setdiff1d(trips_array["service_id"], incal, assume_unique=False)
        if diff.shape[0] > 0:
            diff = ",".join([str(x) for x in diff.tolist()])
            self.__fail(f"There are service IDs in trips.txt that are absent in the calendar -> {diff}")

        self.trips = {str(x): [] for x in np.unique(trips_array["route_id"])}

        for i, line in enumerate(trips_array):
            self.signal.emit(["update", "secondary", i + 1, msg_txt, self.__mt])
            trip = Trip()
            trip._populate(line, trips_array.dtype.names)
            trip.route_id = self.routes[trip.route].route_id
            trip.shape = self.shapes.get(trip.shape_id, trip.shape)
            if trip.trip in trip_replacements:
                all_trips = []
                for trp in trip_replacements[trip.trip]:
                    trip_clone = deepcopy(trip)
                    trip_clone.trip = trp
                    all_trips.append(trip_clone)
            else:
                all_trips = [trip]

            for trip in all_trips:
                stop_times = self.stop_times.get(trip.trip, [])
                if len(stop_times) < 2:
                    logging.warning(f"Trip {trip.trip} had less than two stops, so we skipped it.")
                    continue

                # Drops sequences of links that repeats along a route, keeping the first
                cleaner = stop_times.assign(seqkey=stop_times.stop.shift(-1) + "#####" + stop_times.stop)
                cleaner.drop_duplicates(["seqkey"], inplace=True, keep="first")
                stop_times = cleaner.drop(columns=["seqkey"])
                stop_times["arrival_time"] = stop_times.arrival_time.astype(int)
                stop_times["departure_time"] = stop_times.departure_time.astype(int)
                self.stop_times[trip.trip] = stop_times
                trip.stops = list(stop_times.stop_id.values)
                m = hashlib.md5()
                m.update(trip.route.encode())
                m.update("".join(stop_times.stop.values).encode())

                trip.pattern_hash = m.hexdigest()
                trip.arrivals = list(stop_times.arrival_time.values)
                trip.departures = list(stop_times.departure_time.values)
                trip.source_time = list(stop_times.source_time.values)
                logging.debug(f"{trip.trip} has {len(trip.stops)} stops")
                trip._stop_based_shape = LineString([self.stops[x].geo for x in trip.stops])
                trip.shape = self.shapes.get(trip.shape_id)
                self.trips[trip.route] = self.trips.get(trip.route, [])
                self.trips[trip.route].append(trip)

    def __load_frequencies(self):
        logging.debug("Starting __load_frequencies")

        # GTFS Frequencies table
        freqtxt = "frequencies.txt"
        if freqtxt not in self.zip_archive.namelist():
            return {}

        logging.debug('    Loading "frequencies" table')
        trip_replacements = {}
        with self.zip_archive.open(freqtxt, "r") as file:
            arr = parse_csv(file, column_order[freqtxt])
            freqs = pd.DataFrame(arr) if arr.shape[0] else pd.DataFrame([], columns=column_order[freqtxt])
        self.data_arrays[freqtxt] = freqs

        if freqs.headway_secs.astype(float).min() < 0:
            self.__fail("Non-positive headway found on table frequencies.txt")

        for trid, trip_segments in freqs.groupby(["trip_id"]):
            trip_id = trid[0]
            if trip_id not in self.stop_times:
                self.__fail(f"trip id {trip_id} in frequency table has no corresponding entry in trips")

            # delete the template stop times entry because it's not a real trip
            template = self.stop_times.pop(trip_id)
            trip_replacements[trip_id] = []
            for _, rec in trip_segments.iterrows():
                start_seconds = to_seconds(rec.start_time)
                end_seconds = to_seconds(rec.end_time)
                headway = int(rec.headway_secs)

                # If headway is larger than interval duration we shrink the headway to the duration
                if headway > end_seconds - start_seconds:
                    headway = end_seconds - start_seconds
                # Number of steps (trips to be added) is at least one, and usually higher
                steps = int((end_seconds - start_seconds) / headway)
                # loop over the template according to the frequencies specs to construct the real trips
                for step in range(steps):
                    # We are adding a shift to make the first trip start from headway/2
                    shift = step * headway + headway / 2
                    new_trip = template.copy()
                    if new_trip.arrival_time.max() < start_seconds:
                        shift += start_seconds
                    new_trip.loc[:, "arrival_time"] += shift
                    new_trip.loc[:, "departure_time"] += shift
                    new_trip_str = f"{trip_id}-{new_trip.arrival_time.values[0]}".replace(":", "")
                    self.stop_times[new_trip_str] = new_trip
                    trip_replacements[trip_id].append(new_trip_str)
        return trip_replacements

    def __load_stop_times(self):
        logging.debug("Starting __load_stop_times")

        # GTFS Stop Times table
        self.stop_times.clear()
        logging.debug('    Loading "stop times" table')
        stoptimestxt = "stop_times.txt"
        with self.zip_archive.open(stoptimestxt, "r") as file:
            stoptimes = parse_csv(file, column_order[stoptimestxt])
        self.data_arrays[stoptimestxt] = stoptimes
        msg_txt = f"Load stop times - {self.agency.agency}"

        df = pd.DataFrame(stoptimes)
        for col in ["arrival_time", "departure_time"]:
            df2 = df[col].str.split(":", expand=True)
            df2.fillna(0, inplace=True)
            df2.columns = ["h", "m", "s"]
            df2.loc[df2.h.str.len() < 1, "h"] = 0
            df2.loc[df2.m.str.len() < 1, "m"] = 0
            df2.loc[df2.s.str.len() < 1, "s"] = 0
            df2 = df2.assign(sec=0)
            df2.loc[:, "sec"] = df2.h.astype(int) * 3600 + df2.m.astype(int) * 60 + df2.s.astype(int)
            stoptimes[col] = df2.sec.values

        # We check if there are repeated stop sequence identifiers for a single route
        key = np.core.defchararray.add(stoptimes["trip_id"].astype(str), np.array(["##"] * stoptimes.shape[0]))
        key = np.core.defchararray.add(key, stoptimes["stop_sequence"].astype(str))
        if np.unique(key).shape[0] < stoptimes.shape[0]:
            self.__fail("There are repeated stop_sequences for a single trip_id on stop_times.txt")

        df = pd.DataFrame(stoptimes)

        # Eliminate differences between arrival and departure
        df.loc[:, "arrival_time"] = df.loc[:, ["arrival_time", "departure_time"]].max(axis=1)
        df.loc[:, "departure_time"] = df.loc[:, "arrival_time"]

        counter = df.shape[0]
        df = df.assign(other_stop=df.stop_id.shift(-1), other_trip=df.trip_id.shift(-1))
        df = df.loc[~((df.other_stop == df.stop_id) & (df.trip_id == df.other_trip)), :]
        counter -= df.shape[0]
        df.drop(columns=["other_stop", "other_trip"], inplace=True)
        df.columns = ["stop" if x == "stop_id" else x for x in df.columns]

        stops = [s.stop for s in self.stops.values()]
        stop_ids = [s.stop_id for s in self.stops.values()]
        stop_list = pd.DataFrame({"stop": stops, "stop_id": stop_ids})
        df = df.merge(stop_list, on="stop")
        df.sort_values(["trip_id", "stop_sequence"], inplace=True)
        df = df.assign(source_time=0)  # Means that the stop time came from the original data
        self.signal.emit(["start", "secondary", df.trip_id.unique().shape[0], msg_txt, self.__mt])
        for trip_id, data in [[trip_id, x] for trip_id, x in df.groupby(df["trip_id"])]:
            data.loc[:, "stop_sequence"] = np.arange(data.shape[0])
            self.stop_times[trip_id] = data
            counter += data.shape[0]
            self.signal.emit(["update", "secondary", counter, msg_txt, self.__mt])

    def __load_stops_table(self):
        logging.debug("Starting __load_stops_table")

        # GTFS Stops table
        logging.debug('    Loading "stops" table')
        self.stops = {}
        stopstxt = "stops.txt"
        with self.zip_archive.open(stopstxt, "r") as file:
            stops = parse_csv(file, column_order[stopstxt])
        self.data_arrays[stopstxt] = stops

        # If Stop IDs are unique
        if np.unique(stops["stop_id"]).shape[0] < stops.shape[0]:
            self.__fail("There are repeated Stop IDs in stops.txt")

        # We apply the projection  we have for our network
        lons, lats = self.transformer.transform(stops[:]["stop_lat"], stops[:]["stop_lon"])
        stops[:]["stop_lat"][:] = lats[:]
        stops[:]["stop_lon"][:] = lons[:]

        msg_txt = f"Load stops - {self.agency.agency}"
        self.signal.emit(["start", "secondary", stops.shape[0], msg_txt, self.__mt])
        for i, line in enumerate(stops):
            self.signal.emit(["update", "secondary", i + 1, msg_txt, self.__mt])
            s = Stop(self.agency.agency_id)
            s.populate(line, stops.dtype.names)
            s.agency = self.agency.agency
            s.srid = self.srid
            s.get_node_id()
            self.stops[s.stop_id] = s

    def __load_routes_table(self):
        logging.debug("Starting __load_routes_table")

        # GTFS Routes table
        logging.debug('    Loading "routes" table')
        self.routes = {}
        routetxt = "routes.txt"
        with self.zip_archive.open(routetxt, "r") as file:
            routes = parse_csv(file, column_order[routetxt])
        self.data_arrays[routetxt] = routes

        if np.unique(routes["route_id"]).shape[0] < routes.shape[0]:
            self.__fail("There are repeated route IDs in routes.txt")

        msg_txt = f"Load Routes - {self.agency.agency}"
        self.signal.emit(["start", "secondary", len(routes), msg_txt, self.__mt])

        cap = self.__capacities__.get("other", [None, None, None])
        routes = pd.DataFrame(routes)
        routes = routes.assign(seated_capacity=cap[0], design_capacity=cap[1], total_capacity=cap[2], srid=self.srid)
        for route_type, cap in self.__capacities__.items():
            routes.loc[routes.route_type == route_type, ["seated_capacity", "design_capacity", "total_capacity"]] = cap

        for i, line in routes.iterrows():
            self.signal.emit(["update", "secondary", i + 1, msg_txt, self.__mt])
            r = Route(self.agency.agency_id)
            r.get_route_id()
            r.populate(line.values, routes.columns)
            self.routes[r.route] = r

    def __load_feed_calendar(self):
        logging.debug("Starting __load_feed_calendar")

        # GTFS Calendar table
        logging.debug('    Loading "calendar" table')
        self.services.clear()

        caltxt = "calendar.txt"
        caldatetxt = "calendar_dates.txt"

        if all(x not in self.zip_archive.namelist() for x in [caltxt, caldatetxt]):
            raise FileNotFoundError("GTFS feed MUST contain either calendar or calendar_dates")

        if caltxt in self.zip_archive.namelist():
            with self.zip_archive.open(caltxt, "r") as file:
                calendar = parse_csv(file, column_order[caltxt])
            self.data_arrays[caltxt] = calendar
            if np.unique(calendar["service_id"]).shape[0] < calendar.shape[0]:
                self.__fail("There are repeated service IDs in calendar.txt")

            min_date = min(calendar["start_date"].tolist())
            max_date = max(calendar["end_date"].tolist())
            self.feed_dates = create_days_between(format_date(min_date), format_date(max_date))

            for line in calendar:
                service = Service()
                service._populate(line, calendar.dtype.names)
                self.services[service.service_id] = service

            # GTFS Calendar Dates table
            logging.debug('    Loading "calendar dates" table')

        if caldatetxt not in self.zip_archive.namelist():
            return

        with self.zip_archive.open(caldatetxt, "r") as file:
            caldates = parse_csv(file, column_order[caldatetxt])

        if caldates.shape[0] == 0:
            return

        ordercal = list(column_order[caldatetxt].keys())
        exception_inconsistencies = 0
        for line in range(caldates.shape[0]):
            service_id, sd, exception_type = list(caldates[line][ordercal])

            # convert dates to our standard date format convention
            sd = format_date(sd)

            if service_id not in self.services:
                s = Service()
                s.service_id = service_id
                self.services[service_id] = s
                msg = "           Service ({}) exists on calendar_dates.txt but not on calendar.txt"
                logging.debug(msg.format(service_id))
                exception_inconsistencies += 1

            service = self.services[service_id]

            # adding a service for this specific date
            if exception_type == 1:
                if sd not in service.dates:
                    service.dates.append(sd)
                else:
                    exception_inconsistencies += 1
                    msg = "ignoring service ({}) addition on a day when the service is already active"
                    logging.debug(msg.format(service.service_id))
            elif exception_type == 2:
                # removing a service for this specific date
                if sd in service.dates:
                    _ = service.dates.remove(sd)
                else:
                    exception_inconsistencies += 1
                    msg = "ignoring service ({}) removal on a day from which the service was absent"
                    logging.debug(msg.format(service.service_id))
            else:
                self.__fail(f"illegal service exception type. {service.service_id}")
            self.services[service_id] = service
        if exception_inconsistencies:
            logging.info("    Minor inconsistencies found between calendar.txt and calendar_dates.txt")
        self._exception_inconsistencies = exception_inconsistencies

    def __fail(self, msg: str) -> None:
        logging.error(msg)
        raise ValueError(msg)
