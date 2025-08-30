# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path

import numpy as np
from shapely import LineString

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import commit_and_close, read_and_close


class RoadConnectors:
    """Class for building virtual Road Connectors

    ::

        from polaris.network.traffic.road_connectors import RoadConnectors
        rc = RoadConnectors()
        rc.open(supply_path=path/to/network)

        # We can connect ferries
        rc.connect_ferries(max_distance=50) # Let's use connectors up to 50m only
    """

    def __init__(self, supply_path: Path) -> None:
        self._network_file = supply_path

    def connect_ferries(self, max_distance: int, speed: float = 10.0) -> None:
        """Connect ferries

        Args:
            max_distance (int): Maximum distance to connect.
        """
        purpose = "ferry_connection"
        dtc = DataTableAccess(self._network_file)
        with read_and_close(self._network_file, spatial=True) as conn:
            stops = dtc.get("Transit_Stops", conn).query("route_type in (4, 1200)")

            if stops.empty:
                logging.info("No ferries to connect")
                return

            srid = get_srid(conn=conn)
            rc_val = conn.execute("select coalesce(5000001, max(road_connector) + 1) from Road_Connectors").fetchone()[
                0
            ]
            auto_types = dtc.get("Link_Type", conn).link_type.to_numpy()  # noqa: F841
            links = dtc.get("Link", conn).query("type in @auto_types")

            valid_nodes = np.unique(np.hstack((links.node_a.to_numpy(), links.node_b.to_numpy())))  # noqa: F841
            nodes = dtc.get("Node", conn).query("node in @valid_nodes")

        stops = stops[["stop_id", "geo"]]
        nodes = nodes[["node", "geo"]]
        rconn = stops.sjoin_nearest(nodes, max_distance=max_distance).drop_duplicates(subset=["stop_id"])
        if rconn.empty:
            logging.error(f"No ferry stops within {max_distance}m from the nearest auto network node")
            return

        nodes.rename_geometry("left_geo", inplace=True)
        rconn = rconn.merge(nodes, on="node")
        rconn["conn_geo"] = rconn.apply(lambda row: LineString((row["left_geo"], row["geo"])).wkb, axis=1)
        rconn = rconn.assign(
            road_connector=np.arange(rconn.shape[0]) + rc_val, purpose=purpose, srid=srid, fspd_ab=speed, fspd_ba=speed
        )
        rconn = rconn.rename(columns={"stop_id": "to_node", "node": "from_node"}).drop(columns=["left_geo", "geo"])
        cols = ["road_connector", "from_node", "to_node", "fspd_ab", "fspd_ba", "purpose", "conn_geo", "srid"]
        data = rconn[cols].to_records(index=False)

        sql = """INSERT into Road_Connectors(road_connector, from_node, to_node, "length", fspd_ab, fspd_ba, purpose, geo)
                             VALUES(?,?,?,0, ?, ?,?, GeomFromWKB(?, ?));"""
        with commit_and_close(self._network_file, spatial=True) as conn:
            conn.execute("Delete from Road_Connectors where purpose = ?", [purpose])
            conn.commit()
            conn.executemany(sql, data)

        if rconn.shape[0] < stops.shape[0]:
            logging.error(f"There are Ferry stops farther than {max_distance}m from the nearest auto network node")
            logging.error(f"Only {rconn.shape[0]} out of {stops.shape[0]} stops were connected")
