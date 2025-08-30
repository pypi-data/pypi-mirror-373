# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import os
import sqlite3
import zipfile
from os.path import join
from typing import List

import pandas as pd

from polaris.network.starts_logging import logger
from polaris.network.tools.geo import Geo
from polaris.network.transit.gtfs_writer.agency_writer import write_agencies
from polaris.network.transit.gtfs_writer.fare_writer import write_fares
from polaris.network.transit.gtfs_writer.routes_writer import write_routes
from polaris.network.transit.gtfs_writer.shape_writer import write_shapes
from polaris.network.transit.gtfs_writer.stop_times_writer import write_stop_times
from polaris.network.transit.gtfs_writer.stops_writer import write_stops
from polaris.network.transit.gtfs_writer.trips_writer import write_trips
from polaris.network.transit.route_system_reader.agency_reader import read_agencies
from polaris.network.transit.route_system_reader.pattern_reader import read_patterns
from polaris.network.transit.route_system_reader.routes_reader import read_routes
from polaris.network.transit.route_system_reader.stop_reader import read_stops
from polaris.network.transit.route_system_reader.stop_times_reader import read_stop_times
from polaris.network.transit.route_system_reader.trips_reader import read_trips
from polaris.network.transit.transit_elements.agency import Agency
from polaris.network.transit.transit_elements.pattern import Pattern
from polaris.network.transit.transit_elements.route import Route
from polaris.network.transit.transit_elements.stop import Stop
from polaris.network.transit.transit_elements.trip import Trip
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.utils.database.db_utils import read_and_close


class RouteSystem:
    def __init__(self, database_path: os.PathLike):

        self.__database_path = database_path
        self.dts = DataTableAccess(self.__database_path)

        self.agencies: List[Agency] = []
        self.stops: List[Stop] = []
        self.routes: List[Route] = []
        self.trips: List[Trip] = []
        self.patterns: List[Pattern] = []
        self.stop_times = pd.DataFrame([])

        # self.fare_attributes: List[FareAttributes] = []
        # self.fare_rules: List[FareRule] = []
        # self.zones: List[TransitZone] = []
        self.target_crs = 4326

    def load_route_system(self):
        with read_and_close(self.__database_path, spatial=True) as conn:
            self._read_agencies(conn)
            self._read_stops(conn)
            self._read_routes(conn)
            self._read_patterns(conn)
            self._read_trips(conn)
            self._read_stop_times(conn)

    def _read_agencies(self, conn: sqlite3.Connection):
        self.agencies = read_agencies(conn, self.__database_path)

    def _read_stops(self, conn: sqlite3.Connection):
        self.stops = read_stops(conn, self.target_crs, self.__database_path)

    def _read_routes(self, conn: sqlite3.Connection):
        self.routes = read_routes(conn, self.__database_path)

    def _read_patterns(self, conn: sqlite3.Connection):
        self.patterns = self.patterns or read_patterns(conn, self.target_crs, self.__database_path)

    def _read_trips(self, conn: sqlite3.Connection):
        self.trips = self.trips or read_trips(conn, self.__database_path)

    def _read_stop_times(self, conn: sqlite3.Connection):
        self.stop_times = read_stop_times(conn, self.__database_path)

    def write_GTFS(self, path_to_folder: str):
        """ """
        with read_and_close(self.__database_path, spatial=True) as conn:
            timezone = self._timezone()
            write_agencies(self.agencies, path_to_folder, timezone)
            write_stops(self.stops, path_to_folder)
            write_routes(self.routes, path_to_folder)
            write_shapes(self.patterns, path_to_folder)

            write_trips(self.trips, path_to_folder, conn)
            write_stop_times(self.stop_times, path_to_folder)
            write_fares(path_to_folder, conn, self.__database_path)
            self._zip_feed(path_to_folder)

    def _timezone(self, allow_error=True):
        geotool = Geo(self.__database_path)
        try:
            return geotool.get_timezone()
        except Exception as e:
            logger.error("Could not retrieve the correct time zone for GTFS exporter. Using Chicago instead")
            if not allow_error:
                raise e
            return "America/Chicago"

    def _zip_feed(self, path_to_folder: str):
        filename = join(path_to_folder, "polaris_gtfs.zip")
        files = [
            "agency",
            "stops",
            "routes",
            "trips",
            "stop_times",
            "calendar",
            "shapes",
            "fare_attributes",
            "fare_rules",
        ]
        with zipfile.ZipFile(filename, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                zip_file.write(join(path_to_folder, f"{file}.txt"), f"{file}.txt")
                os.unlink(join(path_to_folder, f"{file}.txt"))
