# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import Dict, Any

from polaris.utils.database.db_utils import read_and_close

AGENCY_MULTIPLIER = 1000000000000  # Maximum of 9,999 routes per agency
ROUTE_ID_MULTIPLIER = 100000000  # Maximum of 9,999 patterns per route
PATTERN_ID_MULTIPLIER = 10000  # Maximum of 9,999 trips per pattern
TRIP_ID_MULTIPLIER = 1

OSM_NODE_RANGE = 10000000
TRANSIT_STOP_RANGE = 1000000
WALK_LINK_RANGE = 30000000
BIKE_LINK_RANGE = 40000000
TRANSIT_LINK_RANGE = 20000000

WALK_AGENCY_NAME = "WALKING"
WALK_AGENCY_ID = 1

# 1 for right, -1 for wrong (left)
DRIVING_SIDE = 1


class constants:
    agencies: Dict[str, Any] = {}
    srid: Dict[str, int] = {}
    routes: Dict[int, int] = {}
    patterns: Dict[int, int] = {}
    trips: Dict[int, int] = {}
    pattern_lookup: Dict[int, int] = {}
    stops: Dict[int, int] = {}
    fares: Dict[int, int] = {}
    transit_links: Dict[int, int] = {}

    def initialize(self, network_file):
        with read_and_close(network_file) as conn:
            # Agencies
            sql = "Select coalesce(max(agency_id), -1) from Transit_Agencies;"
            data = conn.execute(sql).fetchone()[0]
            if data > 0:
                self.agencies["agencies"] = data

            # SRID
            srid = conn.execute("select srid from geometry_columns where f_table_name='node'").fetchone()[0]
            self.srid["srid"] = srid

            # Routes & stops
            sql = "Select coalesce(max(route_id), -1) from Transit_Routes where agency_id=? ;"
            sql_stop = "Select coalesce(max(stop_id), -1) from Transit_Stops where agency_id=? ;"
            for agency_id in range(WALK_AGENCY_ID + 1, self.agencies.get("agencies", 0) + 1):
                val = self.routes.get(agency_id, conn.execute(sql, [agency_id]).fetchone()[0])
                if val > 0:
                    self.routes[agency_id] = val

                stopval = self.stops.get(agency_id, conn.execute(sql_stop, [agency_id]).fetchone()[0])
                if val > 0:
                    self.stops[agency_id] = stopval

            # Patterns
            sql = "Select coalesce(max(pattern_id), -1) from Transit_Patterns where route_id=? ;"
            for route_id in conn.execute("select route_id from Transit_Routes").fetchall():
                db_val = conn.execute(sql, [route_id[0]]).fetchone()[0]
                val = self.patterns.get(route_id[0], db_val)
                if val > 0:
                    self.patterns[route_id[0]] = val

            # Trips
            sql = "Select coalesce(max(trip_id), -1) from Transit_Trips where pattern_id=? ;"
            for patt_id in conn.execute("select pattern_id from Transit_Patterns").fetchall():
                val = self.trips.get(patt_id, conn.execute(sql, [patt_id[0]]).fetchone()[0])
                if val > 0:
                    self.trips[patt_id[0]] = val

            # Links
            sql_lnks = "Select coalesce(max(transit_link), -1)  from Transit_Pattern_Links;"
            val_lnk = conn.execute(sql_lnks).fetchone()[0]

            sql_lnks2 = "Select coalesce(max(transit_link), -1)  from Transit_Links;"
            val_lnk2 = conn.execute(sql_lnks2).fetchone()[0]

            if max(val_lnk, val_lnk2) > 0:
                self.transit_links[1] = max(val_lnk, val_lnk2)
