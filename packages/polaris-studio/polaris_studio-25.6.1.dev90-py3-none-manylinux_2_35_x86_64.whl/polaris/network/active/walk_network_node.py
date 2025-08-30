# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from sqlite3 import Connection

import shapely.wkb
from shapely.geometry import Point

from polaris.network.constants import constants, AGENCY_MULTIPLIER, WALK_AGENCY_ID
from polaris.network.utils.srid import get_srid

TRANSIT_STOPS_QRY = "Select stop_id, zone, asbinary(geo) from Transit_Stops"
MICROMOBILITY_QRY = "Select dock_id, zone, asbinary(geo) from Micromobility_Docks"


class WalkNode:
    """Walk nodes are used to represent any point accessible by walking, be that a simple
    node breaking a walkable roadway link, a transit stop or a micromobility dock"""

    def __init__(self, counter=None):
        self.stop_id = -1
        self.stop = "walk_access"
        self.agency_id = WALK_AGENCY_ID
        self.name = "stop access link"
        self.description = "Synthetic stop access link"
        self.street = " "
        self.zone = -1
        self.geo = Point()
        self.box = None
        self.counter = counter
        self.srid = -1
        self.route_type = -1
        self.transit_zone = None
        self.parent_stop = None
        self.has_parking = 0
        self.connecting = "transit"
        self.__get_node_id()

    def populate(self, record):
        self.stop_id = record[0]
        self.zone = record[1]
        self.geo = shapely.wkb.loads(record[2])
        self.box = self.geo.bounds

    def save(self, conn: Connection, srid=None, commit=True):
        if self.connecting != "transit":
            return
        srid_ = srid or get_srid(conn=conn)
        sql = """insert into TRANSIT_STOPS (stop_id, stop, agency_id, x, y, z, name,
                                            parent_station, description, street, zone, transit_zone_id, has_parking,
                                            route_type, geo)
                                             values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,GeomFromWKB(?,?));"""

        conn.execute(sql, self.data + [srid_])
        if commit:
            conn.commit()

    @property
    def data(self):
        return [
            self.stop_id,
            self.stop,
            self.agency_id,
            self.geo.x,
            self.geo.y,
            0,
            self.name,
            self.parent_stop,
            self.description,
            self.street,
            self.zone,
            self.transit_zone,
            self.has_parking,
            self.route_type,
            self.geo.wkb,
        ]

    def __get_node_id(self):
        c = constants()
        # We will renumber them later, so let's work on a different range
        self.stop_id = 1 + c.stops.get(self.agency_id, self.agency_id * AGENCY_MULTIPLIER * 10)
        c.stops[self.agency_id] = self.stop_id
