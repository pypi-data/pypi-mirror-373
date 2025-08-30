# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import ctypes
import logging
import os.path
import warnings
from ctypes import c_float, c_longlong, c_int64, POINTER, c_uint32, byref, c_bool, c_int32
from pathlib import Path
from typing import Optional

import numpy as np
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.router.path_results import PathResults
from polaris.utils.database.db_utils import read_and_close
from polaris.utils.dir_utils import with_dir
from polaris.utils.env_utils import is_windows
from polaris.utils.file_utils import readlines


class BatchRouter:
    def __init__(
        self, convergence_config: ConvergenceConfig, supply_file: Optional[Path] = None, batch_router_lib=None
    ):
        dll = "Batch_Router.dll" if is_windows() else "libBatch_Router.so"
        if convergence_config.polaris_exe is None and batch_router_lib is None:
            raise ValueError(f"Don't know where to find {dll}")

        dll_path = batch_router_lib or Path(convergence_config.polaris_exe).parent / dll
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"{dll_path} is not available")

        with with_dir(dll_path.parent):
            self.__router_dll = ctypes.cdll.LoadLibrary(str(dll_path))
            self._dll_path = dll_path
        self.__supply_path = supply_file
        convergence_config: ConvergenceConfig = convergence_config
        self.load_scenario(convergence_config)

    def load_scenario(self, convergence_config: ConvergenceConfig):
        warnings.warn("Loading scenario into the router. This may take some time")
        scen_name = str(convergence_config.scenario_main)
        db_name = convergence_config.db_name

        with with_dir(convergence_config.data_dir):
            demand, result = f"{db_name}-Demand".encode("utf-8"), f"{db_name}-Result".encode("utf-8")
            if not self.__router_dll.load(demand, result, scen_name.encode("ASCII")):
                log_file = convergence_config.data_dir / "log" / "batch_router.log"
                self.print_log_error(log_file)
                raise RuntimeError(f"There was an error loading the network. See {log_file} for more details")

        with read_and_close(self.__supply_path) as conn:
            self.__traffic_links = sum(conn.execute("select 2 * count(*) from link").fetchone())
            self.__pt_links = sum(conn.execute("select count(*) from transit_walk").fetchone())
            self.__pt_links += sum(conn.execute("select count(*) from Transit_Pattern_Links").fetchone())

    def print_log_error(self, log_file):
        if not log_file.exists():
            logging.error(f"Couldn't find the log file: {log_file}")
        [logging.error("") for i in range(2)]
        logging.error(f"Error while loading, last 20 lines of {log_file}:")
        for l in readlines(log_file)[-20:]:
            logging.error("    " + l)
        [logging.error("") for i in range(2)]

    def multimodal(self, origin, destination, departure_time=28800, mode=4) -> PathResults:
        """Computes the multi-modal shortest path between two locations"""

        return self.__route_multimodal(origin, destination, departure_time, mode)

    def route(self, origin, destination, departure_time=28800, mode=0) -> PathResults:
        """Computes the shortest path between two locations"""

        return self.__route_location(origin, destination, departure_time, mode)

    def route_links(self, link_origin, link_destination, origin_dir=0, destination_dir=0, departure_time=28800, mode=0):
        """Computes the shortest path between two links"""
        assert origin_dir in (0, 1)
        assert destination_dir in (0, 1)
        return self.__route(2 * link_origin + origin_dir, 2 * link_destination + destination_dir, departure_time, mode)

    def __route(self, link_origin, link_destination, departure_time, mode) -> PathResults:
        """computes the routes between two links"""

        tt = c_float(0)
        num_links = c_int64(self.__traffic_links)
        trajectory = np.zeros(self.__traffic_links, dtype=np.uint32)
        ttimes = np.zeros(self.__traffic_links, dtype=np.float32)
        self.__router_dll.compute_route(
            c_longlong(link_origin),
            c_longlong(link_destination),
            c_int64(departure_time),
            c_int32(mode),
            c_bool(True),
            byref(tt),
            ctypes.pointer(num_links),
            trajectory.ctypes.data_as(POINTER(c_uint32)),
            ttimes.ctypes.data_as(POINTER(c_float)),
        )

        travel_time = float(tt.value) if float(tt.value) < 1e30 else np.inf
        directions, trajectory = np.modf(trajectory[: num_links.value] / 2)
        ttimes = ttimes[: num_links.value]
        del num_links, tt

        return PathResults(
            travel_time=travel_time,
            departure=departure_time,
            links=trajectory.astype(int),
            link_directions=np.ceil(directions).astype(int),
            cumulative_time=ttimes,
        )

    def __route_location(self, loc_origin, loc_destination, departure_time, mode) -> PathResults:
        """computes the routes between two locations"""
        tt = c_float(0)
        num_links = c_int64(self.__traffic_links)
        trajectory = np.zeros(self.__traffic_links, dtype=np.uint32)
        ttimes = np.zeros(self.__traffic_links, dtype=np.float32)
        self.__router_dll.compute_location_route(
            c_longlong(loc_origin),
            c_longlong(loc_destination),
            c_int64(departure_time),
            c_int32(mode),
            c_bool(True),
            byref(tt),
            ctypes.pointer(num_links),
            trajectory.ctypes.data_as(POINTER(c_uint32)),
            ttimes.ctypes.data_as(POINTER(c_float)),
        )
        travel_time = float(tt.value) if (float(tt.value) < 1e30 and np.count_nonzero(trajectory)) else np.inf
        directions, trajectory = np.modf(trajectory[: num_links.value] / 2)
        ttimes = ttimes[: num_links.value]
        del num_links, tt

        return PathResults(
            travel_time=travel_time,
            departure=departure_time,
            links=trajectory.astype(int),
            link_directions=np.ceil(directions).astype(int),
            cumulative_time=ttimes,
        )

    def __route_multimodal(self, loc_origin, loc_destination, departure_time, mode) -> PathResults:
        """computes the routes between two locations"""

        tt = c_float(0)
        num_links = c_int64(self.__pt_links)
        trajectory = np.zeros(self.__pt_links, dtype=np.uint32)
        ttimes = np.zeros(self.__traffic_links, dtype=np.float32)
        self.__router_dll.compute_multimodal_route(
            c_longlong(loc_origin),
            c_longlong(loc_destination),
            c_int64(departure_time),
            c_int32(mode),
            c_bool(True),
            byref(tt),
            ctypes.pointer(num_links),
            trajectory.ctypes.data_as(POINTER(c_uint32)),
            ttimes.ctypes.data_as(POINTER(c_float)),
        )

        travel_time = float(tt.value) if float(tt.value) < 1e30 else np.inf
        directions, trajectory = np.modf(trajectory[: num_links.value] / 2)
        ttimes = ttimes[: num_links.value]
        del num_links, tt

        return PathResults(
            travel_time=travel_time,
            departure=departure_time,
            links=trajectory.astype(int),
            link_directions=np.ceil(directions).astype(int),
            cumulative_time=ttimes,
        )
