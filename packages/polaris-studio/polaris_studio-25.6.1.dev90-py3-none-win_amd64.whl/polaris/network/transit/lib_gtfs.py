# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from copy import deepcopy
import logging
from typing import Dict, List, Optional, Any

import pandas as pd
from polaris.network.constants import constants, PATTERN_ID_MULTIPLIER
from polaris.network.utils.srid import get_srid
from polaris.network.utils.worker_thread import WorkerThread
from polaris.utils.database.db_utils import commit_and_close
from polaris.utils.optional_deps import check_dependency
from polaris.utils.signals import SIGNAL
from shapely.geometry import Point, MultiLineString
from .functions.create_raw import create_raw_shapes
from .functions.path_storage import PathStorage
from .gtfs_loader import GTFSReader
from .map_matching_graph import MMGraph
from .transit_elements.link import Link
from .transit_elements.mode_correspondence import mode_correspondence
from .transit_elements.pattern import Pattern
from .transit_elements.route import Route
from .transit_elements.stop import Stop
from .transit_elements.trip import Trip


class GTFSRouteSystemBuilder(WorkerThread):
    """Container for GTFS feeds providing data retrieval for the importer

    ::

        from polaris.network.network import Network

        network_path = 'D:/Argonne/GTFS/CHICAGO/chicago2018-Supply.sqlite'
        GTFS_path = 'D:/Argonne/GTFS/CHICAGO/METRA/2019-10-04.zip'

        my_network = Network()
        my_network.open(network_path)

        transit = my_network.transit()

        feed = transit.new_gtfs(file_path=GTFS_path
                                description='METRA Commuter Rail',
                                agency_identifier='METRA')

        # In case you created the feed without providing an agency ID or description
        feed.set_description('METRA Commuter Air Force')

        # For a least of all dates covered by this feed
        feed.dates_available()

        # If you set it with the wrong feed and want to change it
        feed.set_feed('D:/Argonne/GTFS/CHICAGO/METRA/2073-12-03.zip')

        # To prevent map-matching to be performed and execute a faster import
        feed.set_allow_map_match(False)

        feed.load_date('2019-10-15')

        # To save the transit raw-shapes to the database for later consult
        feed.create_raw_shapes()

        # To map-match the services in this feed
        feed.map_match()
        feed.execute_import()
    """

    signal = SIGNAL(object)

    def __init__(self, network, agency_id, file_path, day="", description="", capacities: Optional[dict] = None):
        """Instantiates a transit class for the network

        Args:

            *polaris network* (:obj:`Network`): Supply model to which this GTFS will be imported
            *agency_identifier* (:obj:`str`): ID for the agency this feed refers to (e.g. 'CTA')
            *file_path* (:obj:`str`): Full path to the GTFS feed (e.g. 'D:/project/my_gtfs_feed.zip')
            *day* (:obj:`str`, *Optional*): Service data contained in this field to be imported (e.g. '2019-10-04')
            *description* (:obj:`str`, *Optional*): Description for this feed (e.g. 'CTA19 fixed by John after coffee')
        """
        WorkerThread.__init__(self, None)
        check_dependency("pyproj")
        import pyproj
        from pyproj import Transformer

        default_capacities = capacities or {}
        self.__network = network
        self.geotool = network.geotools
        self.archive_dir = ""  # type: str
        self.day = ""  # This is update below.
        self.gtfs_data = GTFSReader(network.path_to_file)

        self.srid = get_srid(network.path_to_file)
        self.transformer = None
        self.wgs84 = pyproj.Proj("epsg:4326")
        self.trip_by_service: Dict[str, Trip] = {}
        self.patterns: Dict[int, Pattern] = {}
        self.graphs: Dict[int, Any] = {}
        self.srid = network.srid
        self.transformer = Transformer.from_crs("epsg:4326", f"epsg:{self.srid}", always_xy=False)
        self.sridproj = pyproj.Proj(f"epsg:{self.srid}")
        self.gtfs_data.agency.agency = agency_id
        self.gtfs_data.agency.description = description
        self.__default_capacities = default_capacities
        self.__do_raw_shapes__ = False
        self.__do_execute_map_matching = False
        self.__outside_zones = 0
        self.path_store = PathStorage()
        self._path_to_file = network.path_to_file
        self.__load_executed = False

        if file_path is not None:
            logging.info(f"Creating GTFS feed object for {file_path}")
            self.gtfs_data.set_feed_path(file_path)
            self.gtfs_data._set_capacities(self.__default_capacities)

        self.select_routes: Dict[int, Route] = {}
        self.select_trips: List[Trip] = []
        self.select_stops: Dict[int, Stop] = {}
        self.select_patterns: Dict[int, Pattern] = {}
        self.select_links: Dict[str, Link] = {}
        self.__mt = ""

        if day:
            self.load_date(day)

    def set_capacities(self, capacities: dict):
        """Sets default capacities for modes/vehicles.

        Args:
            *capacities* (:obj:`dict`): Dictionary with GTFS types as keys, each with a list
                                        of 3 items for values for capacities: seated, design and total
                                        i.e. -> "{0: [150, 300, 300],...}"
        """
        self.gtfs_data._set_capacities(capacities)

    def set_maximum_speeds(self, max_speeds: pd.DataFrame):
        """Sets the maximum speeds to be enforced at segments.

        Args:
            *max_speeds* (:obj:`pd.DataFrame`): Requires 4 fields: mode, min_distance, max_distance, speed.
            Modes not covered in the data will not be touched and distance brackets not covered will receive
            the maximum speed, with a warning
        """
        dict_speeds = {idx[0]: df for idx, df in max_speeds.groupby(["mode"])}  # noqa: C416
        self.gtfs_data._set_maximum_speeds(dict_speeds)

    def dates_available(self) -> list:
        """Returns a list of all dates available for this feed

        Returns:
            *feed dates* (:obj:`list`): list of all dates available for this feed
        """
        return deepcopy(self.gtfs_data.feed_dates)

    def set_allow_map_match(self, allow=True):
        """Changes behavior for finding transit-link shapes

        Defaults to True

        Args:
              *allow* (:obj:`bool` *optional*): If True, allows uses map-matching in search of precise
              transit_link shapes. If False, sets transit_link shapes equal to straight lines between
              stops. In the presence of GTFS raw shapes it has no effect.
        """

        self.__do_execute_map_matching = allow

    def map_match(self, route_types: Optional[List[int]] = None) -> None:
        """Performs map-matching for all routes of one or more types

        Defaults to map-matching Bus routes (type 3) only
        For a reference of route types, see https://developers.google.com/transit/gtfs/reference#routestxt

        Args:
              *route_types* (:obj:`List[int]` or :obj:`Tuple[int]`): Default is [3], for bus only
        """
        rtp = route_types or [3]
        if not isinstance(rtp, list) and not isinstance(rtp, tuple) and not isinstance(rtp, set):
            raise TypeError("Route_types must be list or tuple")

        if any(not isinstance(item, int) for item in rtp):
            raise TypeError("All route types must be integers")

        mt = f"Map-matching routes for {self.gtfs_data.agency.agency}"
        self.signal.emit(["start", "secondary", len(self.select_patterns.keys()), "Map-matching", mt])
        for i, pat in enumerate(self.select_patterns.values()):
            self.signal.emit(["update", "secondary", i + 1, "Map-matching", mt])
            if pat.route_type in rtp:
                pat.map_match()
        self.path_store.clear()

    def set_agency_identifier(self, agency_id: str) -> None:
        """Adds agency ID to this GTFS for use on import

        Args:
            *agency_id* (:obj:`str`): ID for the agency this feed refers to (e.g. 'CTA')
        """
        self.gtfs_data.agency.agency = agency_id

    def set_feed(self, feed_path: str) -> None:
        """Sets GTFS feed source to be used

        Args:
            *file_path* (:obj:`str`): Full path to the GTFS feed (e.g. 'D:/project/my_gtfs_feed.zip')
        """
        self.gtfs_data.set_feed_path(feed_path)
        self.gtfs_data.agency.feed_date = self.gtfs_data.feed_date

    def set_description(self, description: str) -> None:
        """Adds description to be added to the imported layers metadata

        Args:
            *description* (:obj:`str`): Description for this feed (e.g. 'CTA2019 fixed by John Doe after strong coffee')
        """
        self.description = description

    def set_date(self, service_date: str) -> None:
        """Sets the date for import without doing any of data processing, which is left for the importer"""
        self.day = service_date

    def load_date(self, service_date: str) -> None:
        """Loads the transit services available for *service_date*

        Args:
            *service_date* (:obj:`str`): Day for which services are to be imported (e.g. '2019-10-04')
        """
        if service_date == self.day and self.__load_executed:
            return
        if self.srid is None:
            raise ValueError("We cannot load data without an SRID")
        # load the feed and mark it as loaded
        if service_date not in self.gtfs_data.feed_dates:
            raise ValueError("The date chosen is not available in this GTFS feed")
        self.day = service_date

        self.gtfs_data.load_data(service_date)

        logging.info("  Building data structures")
        self.__build_data()
        self.gtfs_data.agency.service_date = self.day
        self.__load_executed = True

    def set_do_raw_shapes(self, do_shapes: bool):
        """Sets the raw shapes importer to True for execution by the importer"""
        self.__do_raw_shapes__ = do_shapes

    def create_raw_shapes(self):
        """Adds all shapes provided in the GTFS feeds to the TRANSIT_RAW_SHAPES table in the network file

        This table is for debugging purposes, as allows the user to compare it with the result of the
        map-matching procedure.

        All previously existing entries with this feed's prefix ID are removed.
        For patterns with no corresponding shape on *shapes.txt* or in the absence of *shapes.txt*,
        the raw shape is generated by connecting stops directly.
        """

        with commit_and_close(self.__network.path_to_file, spatial=True) as conn:
            create_raw_shapes(self.gtfs_data.agency.agency_id, self.select_patterns, conn)
        self.__do_raw_shapes__ = False

    def doWork(self):
        """Alias for execute_import"""
        self.execute_import()
        self.finished()

    def execute_import(self):
        logging.debug("Starting execute_import")

        if self.day:
            self.load_date(self.day)
        if not self.select_routes:
            logging.warning(f"Nothing to import for {self.gtfs_data.agency.agency} on {self.day}")
            return

        logging.info(f"  Importing feed for agency {self.gtfs_data.agency.agency} on {self.day}")
        self.__mt = f"Importing {self.gtfs_data.agency.agency} to supply"
        self.signal.emit(["start", "master", 4 + self.__do_raw_shapes__, self.__mt])

        self.save_to_disk()

        if self.__do_execute_map_matching:
            logging.info(f"{self.path_store.uses:,} paths requested. {self.path_store.total_paths:,} objects created")
        self.path_store.clear()

    def save_to_disk(self):
        """Saves all transit elements built in memory to disk"""

        if self.__do_raw_shapes__:
            self.create_raw_shapes()

        with commit_and_close(self.__network.path_to_file, spatial=True) as conn:
            st = f"Importing routes for {self.gtfs_data.agency.agency}"
            self.signal.emit(["start", "secondary", len(self.select_routes.keys()), st, self.__mt])
            for counter, (_, route) in enumerate(self.select_routes.items()):  # type: Route
                route.save_to_database(conn, commit=False)
                self.signal.emit(["update", "secondary", counter + 1, st, self.__mt])
            conn.commit()

            st = f"Importing patterns for {self.gtfs_data.agency.agency}"
            self.signal.emit(["start", "secondary", len(self.select_patterns.keys()), st, self.__mt])
            for counter, (_, pattern) in enumerate(self.select_patterns.items()):  # type: Pattern
                pattern.save_to_database(conn, commit=False)
                self.signal.emit(["update", "secondary", counter + 1, st, self.__mt])
            conn.commit()

            self.gtfs_data.agency.save_to_database(conn)
            st = f"Importing trips for {self.gtfs_data.agency.agency}"
            self.signal.emit(["start", "secondary", len(self.select_trips), st, self.__mt])
            for counter, trip in enumerate(self.select_trips):  # type: Trip
                trip.save_to_database(conn, commit=False)
                self.signal.emit(["update", "secondary", counter + 1, st, self.__mt])
            conn.commit()

            st = f"Importing links for {self.gtfs_data.agency.agency}"
            self.signal.emit(["start", "secondary", len(self.select_links.keys()), st, self.__mt])
            for counter, (_, link) in enumerate(self.select_links.items()):  # type: Link
                link.save_to_database(conn, commit=False)
                self.signal.emit(["update", "secondary", counter + 1, st, self.__mt])
            conn.commit()

            self.__outside_zones = 0
            zone_ids1 = {x.origin: x.origin_id for x in self.gtfs_data.fare_rules if x.origin_id >= 0}
            zone_ids2 = {x.destination: x.destination_id for x in self.gtfs_data.fare_rules if x.destination_id >= 0}
            zone_ids = {**zone_ids1, **zone_ids2}
            st = f"Importing stops for {self.gtfs_data.agency.agency}"
            self.signal.emit(["start", "secondary", len(self.select_stops.keys()), st, self.__mt])
            has_ferries = False
            for counter, (_, stop) in enumerate(self.select_stops.items()):  # type: Stop
                if stop.zone in zone_ids:
                    stop.zone_id = zone_ids[stop.zone]
                stop.taz = self.geotool.get_geo_item("zone", stop.geo)
                stop.save_to_database(conn, commit=False)
                if stop.route_type in [4, 1200]:
                    has_ferries = True
                self.signal.emit(["update", "secondary", counter + 1, st, self.__mt])
            conn.commit()
            # Fare data
            for fare in self.gtfs_data.fare_attributes.values():
                fare.save_to_database(conn)

            for fare_rule in self.gtfs_data.fare_rules:
                fare_rule.save_to_database(conn)

            zones = [[y, x, self.gtfs_data.agency.agency_id] for x, y in list(zone_ids.items())]
            if zones:
                sql = "Insert into Transit_Zones(transit_zone_id, transit_zone, agency_id) values(?, ?, ?);"
                conn.executemany(sql, zones)
            conn.commit()

        if self.__outside_zones:
            msg = "    Some stops are outside the zoning system. Check the result on a map and see the log for info"
            logging.warning(msg)

        if has_ferries:
            msg = "    We found ferries in your GTFS. You must add Road Connetors for them to allow cars to cross"
            logging.warning(msg)

    def finished(self):
        self.signal.emit(["finished_static_gtfs_procedure"])

    def __build_data(self):
        logging.debug("Starting __build_data")
        self.__get_routes_by_date()

        # construct the Polaris trip and pattern tables from the list of GTFS sources
        self.select_stops.clear()
        self.select_links.clear()
        self.select_patterns.clear()

        if self.__do_execute_map_matching:
            self.builds_link_graphs_with_broken_stops()

        c = constants()
        msg_txt = f"Building data for {self.gtfs_data.agency.agency}"
        self.signal.emit(["start", "secondary", len(self.select_routes), msg_txt, self.__mt])
        for counter, (route_id, route) in enumerate(self.select_routes.items()):
            self.signal.emit(["update", "secondary", counter + 1, msg_txt, self.__mt])
            new_trips = self._get_trips_by_date_and_route(route_id, self.day)

            all_pats = [trip.pattern_hash for trip in new_trips]
            cntr = route.route_id + PATTERN_ID_MULTIPLIER
            for pat_hash in sorted(set(all_pats)):
                c.pattern_lookup[pat_hash] = cntr

                # We can go back to proper bit coding when we can get 64 bit read in Polaris
                cntr += ((all_pats.count(pat_hash) // 100) + 1) * PATTERN_ID_MULTIPLIER

            self.select_trips.extend(new_trips)
            # We will save each and every trip and all unique patterns to the database
            patterns = []
            for trip in new_trips:
                trip.pattern_id = c.pattern_lookup[trip.pattern_hash]
                trip.get_trip_id()
                logging.debug(f"Trip ID generated is {trip.trip_id} for pattern {trip.pattern_id}")
                if trip.pattern_id in self.select_patterns:
                    continue

                pat = self.__build_new_pattern(route, route_id, trip)
                patterns.append(pat)

            route.shape = self.__build_route_shape(patterns)

    def __build_new_pattern(self, route, route_id, trip) -> Pattern:
        logging.debug(f"New Pattern ID {trip.pattern_id} for route ID {route_id}")
        p = Pattern(self.geotool, route.route_id, self)
        p.pattern_hash = trip.pattern_hash
        p.pattern_id = trip.pattern_id
        p.route = trip.route
        p.route_type = int(route.route_type)
        p.raw_shape = trip.shape
        p._stop_based_shape = trip._stop_based_shape
        for stop_id in self.gtfs_data.stop_times[trip.trip].stop_id.values:
            if stop_id not in self.select_stops:
                stp = self.gtfs_data.stops[stop_id]
                stp.route_type = route.route_type
                stp.stop = stp.stop
                self.select_stops[stop_id] = stp
            p.stops.append(self.gtfs_data.stops[stop_id])
        if self.__do_execute_map_matching:
            p.map_match()
        self.select_patterns[trip.pattern_id] = p

        p.links.clear()
        prev_end = self.gtfs_data.stops[trip.stops[0]].geo
        pgeo = p.best_shape()
        for i in range(1, len(trip.stops)):
            link = Link(self.srid)
            link.pattern_id = trip.pattern_id
            link.get_link_id()
            fnode = trip.stops[i - 1]
            tnode = trip.stops[i]
            link.from_node = fnode
            link.to_node = tnode
            link.build_geo(self.gtfs_data.stops[fnode].geo, self.gtfs_data.stops[tnode].geo, pgeo, prev_end)
            prev_end = Point(list(link.geo.coords)[-1])
            link.type = int(route.route_type)
            p.links.append(link.transit_link)
            self.select_links[link.key] = link

        return p

    def __build_route_shape(self, patterns) -> MultiLineString:
        shapes = [p.best_shape() for p in patterns if p.best_shape() is not None]
        return MultiLineString(shapes)

    def __error_logging(self, titles, values):
        for i, j in zip(titles, values):
            logging.error(f"- {i}: {j}")

    def __warning_logging(self, titles, values):
        for i, j in zip(titles, values):
            logging.warning(f"- {i}: {j}")

    def __fail(self, msg: str) -> None:
        logging.error(msg)
        raise Exception(msg)

    def __get_routes_by_date(self):
        logging.debug("Starting __get_routes_by_date")

        routes = {}
        for route_id, route in self.gtfs_data.routes.items():
            if route_id not in self.gtfs_data.trips:
                continue
            for trip in self.gtfs_data.trips[route_id]:
                service = trip.service_id
                if service not in self.gtfs_data.services.keys():
                    continue
                if self.day in self.gtfs_data.services[service].dates:
                    routes[route_id] = route
                    break
        if not routes:
            logging.warning("NO ROUTES OPERATING FOR THIS DATE")

        for route in routes.values():  # type: Route
            route.agency = self.gtfs_data.agency.agency

        self.select_routes = routes

    def _get_trips_by_date_and_route(self, route_id: int, service_date: str) -> list:
        trips = [
            trip
            for trip in self.gtfs_data.trips[route_id]
            if service_date in self.gtfs_data.services[trip.service_id].dates
        ]
        return sorted(trips)

    def _get_stops_by_date(self, service_date: str) -> dict:
        self.load_date(service_date)
        return self.gtfs_data.stops

    def _get_shapes_by_date(self, service_date: str) -> dict:
        self.load_date(service_date)

        return self.gtfs_data.shapes

    def _get_fare_attributes_by_date(self, service_date: str) -> dict:
        self.load_date(service_date)
        return self.gtfs_data.fare_attributes

    def builds_link_graphs_with_broken_stops(self):
        """Build the graph for links for a certain mode while splitting the closest links at stops' projection

        Args:
            *mode_id* (:obj:`int`): Mode ID for which we will build the graph for
        """

        route_types = list({r.route_type for r in self.select_routes.values()})
        route_types = [mode_id for mode_id in route_types if mode_correspondence[mode_id] not in self.graphs]
        if not route_types:
            return
        mm = MMGraph(self.geotool, self.gtfs_data.stops, self.gtfs_data.agency.agency, self.__mt)
        for mode_id in route_types:
            mode = mode_correspondence[mode_id]
            graph = mm.build_graph_with_broken_stops(mode_id)
            if graph.num_links <= 0:
                continue
            self.graphs[mode] = graph
