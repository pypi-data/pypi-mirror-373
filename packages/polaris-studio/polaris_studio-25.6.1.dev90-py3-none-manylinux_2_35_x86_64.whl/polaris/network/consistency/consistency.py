# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from typing import List

import pandas as pd

from polaris.network.utils.srid import get_srid
from polaris.network.utils.worker_thread import WorkerThread
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.utils.database.db_utils import commit_and_close
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.signals import SIGNAL


class Consistency(WorkerThread):
    consistency = SIGNAL(object)

    def __init__(self, network_file: PathLike):
        from polaris.network.active.active_networks import ActiveNetworks
        from polaris.network.consistency.geo_consistency import GeoConsistency
        from polaris.network.tools.tools import Tools

        WorkerThread.__init__(self, None)
        from polaris.network.tools.geo import Geo

        self.srid = get_srid(network_file)
        self.__network_file = network_file
        self.issues_addressed = 0
        self.errors = pd.DataFrame([])
        self.intersections_to_rebuild: List[int] = []
        self.__max_id__ = -1

        self.master_txt = "Enforcing consistency"
        polaris_logging()

        tables = DataTableAccess(self.__network_file)
        geotools = Geo(network_file)
        self.gc = GeoConsistency(geotools, tables)
        self.tools = Tools(geotools, tables, self.__network_file)
        self.an = ActiveNetworks(geotools, tables)

        self.proc_calls = {
            "update_location_association": {
                "procedure": self.gc.update_location_association,
                "run": False,
            },
            "update_link_association": {
                "procedure": self.gc.update_link_association,
                "run": False,
            },
            "update_active_network_association": {
                "procedure": self.gc.update_active_network_association,
                "run": False,
            },
            "update_area_type_association": {"procedure": self.gc.update_area_type_association, "run": False},
            "update_zone_association": {"procedure": self.gc.update_zone_association, "run": False},
            "update_popsyn_region_association": {"procedure": self.gc.update_popsyn_region_association, "run": False},
            "update_county_association": {"procedure": self.gc.update_county_association, "run": False},
            "rebuild_location_links": {"procedure": self.tools.rebuild_location_links, "run": False},
            "rebuild_location_parking": {"procedure": self.tools.rebuild_location_parking, "run": False},
            "rebuild_intersections": {
                "procedure": self.tools.rebuild_intersections,
                "run": False,
                "args": {"missing_only": True, "signals": "osm"},
            },
            "Active Networks": {"procedure": self.an.build, "run": False},
        }

    def doWork(self, force=False):
        """Alias for execute"""
        self.enforce(force)

    def enforce(self, force=False):
        """Runs through all records on *Geo_Consistency_Controller* and fixes one at a time"""
        with commit_and_close(self.__network_file, spatial=False) as conn:
            errors = pd.read_sql("SELECT * FROM Geo_Consistency_Controller", conn)

        for table, df in errors.groupby("table_name"):
            fields = df["field_changed"].tolist()
            table_name = table.lower()
            if table_name == "location":
                self.set_change_to_locations(fields)
            if table_name == "parking":
                self.set_change_to_parking(fields)
            elif table_name == "zone":
                self.set_change_to_zone(fields)
            elif table_name == "micromobility_docks":
                self.set_change_to_micromobility_docks()
            elif table_name == "transit_stops":
                self.proc_calls["Active Networks"]["run"] = True
            elif table_name in ["transit_bike", "transit_walk"]:
                self.set_change_to_active_networks()
            elif table_name in ["link", "node"]:
                self.set_change_to_links(fields)
            elif table_name in ["counties"]:
                self.proc_calls["update_county_association"]["run"] = True
            elif table_name in ["popsyn_region"]:
                self.proc_calls["update_popsyn_region_association"]["run"] = True
            else:
                raise ValueError(f"Don't know how to fix issues for table {table_name}")

        if self.proc_calls["Active Networks"]["run"]:
            # If we are rebuilding the active networks, we will update the walk and bike links anyways
            self.proc_calls["update_active_network_association"]["run"] = False

        self.__process_queue()
        self.consistency.emit(["finished_consistency_procedure"])

    def set_change_to_locations(self, fields):
        if any(x in fields for x in ["walk_link", "bike_link", "geo"]):
            self.proc_calls["update_active_network_association"]["run"] = True
        if any(x in fields for x in ["link", "geo"]):
            self.proc_calls["update_link_association"]["run"] = True

        if "geo" in fields:
            self.proc_calls["update_location_association"]["run"] = True
            self.proc_calls["rebuild_location_links"]["run"] = True
            self.proc_calls["rebuild_location_parking"]["run"] = True

    def set_change_to_parking(self, fields):
        if "geo" in fields:
            self.proc_calls["rebuild_location_parking"]["run"] = True

    def set_change_to_zone(self, fields: List[str]):
        if "geo" in fields:
            self.proc_calls["update_zone_association"]["run"] = True
        if any(x in fields for x in ["area_type", "geo"]):
            self.proc_calls["update_area_type_association"]["run"] = True

    def set_change_to_micromobility_docks(self):
        self.proc_calls["update_link_association"]["run"] = True

    def set_change_to_active_networks(self):
        self.proc_calls["update_active_network_association"]["run"] = True

    def set_change_to_links(self, fields):
        self.proc_calls["update_active_network_association"]["run"] = True

        self.proc_calls["update_link_association"]["run"] = True

        self.proc_calls["rebuild_location_links"]["run"] = True
        self.proc_calls["rebuild_intersections"]["run"] = True

        if any(x in fields for x in ["type", "geo"]):
            self.proc_calls["Active Networks"]["run"] = True

    def __process_queue(self):
        self.consistency.emit(["start", "master", len(self.proc_calls.keys()), "UPDATING"])
        for i, job in enumerate(self.proc_calls.values()):
            if job["run"]:
                if "args" in job:
                    job["procedure"](**job["args"])
                else:
                    job["procedure"]()
            self.consistency.emit(["update", "master", i + 1, "UPDATING"])
        with commit_and_close(self.__network_file, spatial=False) as conn:
            conn.execute("DELETE FROM Geo_Consistency_Controller")
        self.consistency.emit(["finished_consistency_procedure"])
