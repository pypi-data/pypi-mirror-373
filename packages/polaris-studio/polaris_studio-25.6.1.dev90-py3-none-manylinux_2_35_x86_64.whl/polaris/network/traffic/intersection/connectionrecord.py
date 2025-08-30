# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from sqlite3 import Connection

from shapely.geometry import LineString
from shapely.ops import substring

from polaris.network.traffic.intersection.approximation import Approximation
from .turn_type import turn_type
from polaris.network.utils.srid import get_srid

conn_table_fields = ["link", "dir", "node", "to_link", "to_dir", "lanes", "to_lanes", "type", "approximation", "geo"]


class ConnectionRecord:
    insert_sql = """Insert into Connection(link, dir, node, to_link, to_dir, lanes, to_lanes, "type", approximation, geo)
                             VALUES (?,?,?,?,?,?,?,?,?, GeomFromWKB(?,?))"""
    database_fields = conn_table_fields
    segment_length = 100  # each stub will be up to 100m

    def __init__(self, link: Approximation, to_link: Approximation, lanes="", to_lanes=""):
        self.link = link.link
        self.direction = link.direction
        self.node = link.node
        self.to_link = to_link.link
        self.to_dir = to_link.direction
        self.lanes = str(lanes)
        self.to_lanes = str(to_lanes)
        self.type = turn_type(link, to_link)
        self.penalty = to_link.penalty
        self.speed = 0
        self.capacity = 0
        self.in_high = 0
        self.out_high = 0
        self.approximation = link.cardinal

        self.from_geo = LineString(link.geo)
        self.to_geo = LineString(to_link.geo)

        # We build the geometry of approximation
        # Get both geometries
        from_geo = substring(
            self.from_geo, self.from_geo.length - min(self.from_geo.length, self.segment_length), self.from_geo.length
        )
        to_geo = substring(self.to_geo, 0, min(self.to_geo.length, self.segment_length))

        points = []
        points.extend(from_geo.coords)
        points.extend(to_geo.coords[1:])
        self.geo = LineString(points)

    def save_to_database(self, conn: Connection) -> None:
        """Saves connection record to the database

        Args:
           *conn* (:obj:`Connection`): SQLite connection to the network's database
        """
        data = self.data
        data[-1] = self.geo.wkb
        conn.execute(self.insert_sql, data + [get_srid(conn=conn)])
        conn.commit()

    @property
    def data(self) -> list:
        return [
            self.link,
            self.direction,
            self.node,
            self.to_link,
            self.to_dir,
            self.lanes,
            self.to_lanes,
            self.type,
            self.approximation,
            self.geo,
        ]
