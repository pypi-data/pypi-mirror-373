# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from copy import deepcopy
from sqlite3 import Connection
from typing import List, Any, Tuple

from polaris.network.utils.srid import get_srid
from polaris.utils.optional_deps import check_dependency


class ActiveTransportLink:
    def __init__(self, record: List[Any]):
        check_dependency("shapely")
        import shapely.wkb
        from shapely.geometry import LineString

        self.stops: List[int] = []
        self.__table_name__ = ""
        self.__field_name__ = ""

        self.id: int = record[0]
        if len(record) == 1:
            record = [-1, None, None, None, 0]
        else:
            self.geo: LineString = shapely.wkb.loads(record[5])
            self.box: Tuple[float] = self.geo.bounds
        self.node_a: int = record[1]
        self.node_b: int = record[2]
        self.distance: float = record[3]
        self.ref_link: int = record[4]

    def split(self, distance: float, point_id=None):
        # Straight from https://shapely.readthedocs.io/en/latest/manual.html
        # Cuts a line in two at a distance from its starting point
        from shapely.ops import substring

        if distance <= 0.0 or distance >= self.geo.length:
            return [self]

        a = deepcopy(self)
        a.id = -1
        a.geo = substring(self.geo, 0, distance)
        a.node_b = point_id

        b = deepcopy(self)
        b.id = -1
        b.geo = substring(self.geo, distance, self.geo.length)
        b.node_a = point_id
        return [a, b]

    def save(self, conn: Connection, srid=None, commit=True) -> None:

        srid_ = srid or get_srid(conn=conn)
        sql = f"""INSERT into {self.__table_name__}({self.__field_name__},from_node, to_node, "length", ref_link, geo)
                                                    values(?,?,?,?,?,GeomFromWKB(?, ?))"""

        vals = [self.id, self.node_a, self.node_b, self.geo.length, self.ref_link, self.geo.wkb, srid_]
        conn.execute(sql, vals)
        if commit:
            conn.commit()

    def delete(self, conn: Connection, commit=True) -> None:
        if len(self.__field_name__):
            conn.execute(f"DELETE from {self.__table_name__} where {self.__field_name__}={self.id};")
            if commit:
                conn.commit()

    def __setattr__(self, key, value):
        self.__dict__[key] = value

        if key == "geo":
            self.__dict__["distance"] = self.geo.length
            assert self.distance > 0, "Link has zero length"
