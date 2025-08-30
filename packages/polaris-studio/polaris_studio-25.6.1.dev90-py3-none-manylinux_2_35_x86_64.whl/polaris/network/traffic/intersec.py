# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3
from os import PathLike
from typing import List, Optional
from warnings import warn

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely.wkb
from shapely.geometry import Point

from polaris.network.consistency.link_types_constants import RAMP, FREEWAY, EXPRESSWAY
from polaris.network.osm.osm import OSM
from polaris.network.starts_logging import logger
from polaris.network.traffic.hand_of_driving import get_driving_side
from polaris.network.traffic.intersection.approximation import Approximation
from polaris.network.traffic.intersection.approximation_list import sort_approx_list
from polaris.network.traffic.intersection.connectionrecord import ConnectionRecord, conn_table_fields
from polaris.network.traffic.intersection.connections_top_to_top import connect_two_links_top_to_top
from polaris.network.traffic.intersection.find_directions import find_directions
from polaris.network.traffic.intersection.freeway_intersection import FreewayIntersection
from polaris.network.traffic.intersection.geometric_signal_need import geom_need_for_signal
from polaris.network.traffic.intersection.links_merge import LinksMerge
from polaris.network.traffic.intersection.regular_intersection_connection import GenericIntersection
from polaris.network.traffic.intersection.should_allow import should_allow
from polaris.network.traffic.intersection_control.signal import Signal
from polaris.network.traffic.intersection_control.stop_sign import StopSign
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import read_and_close
from polaris.utils.structure_finder import find_table_fields
from polaris.utils.user_configs import UserConfig


class Intersection:
    """Network intersection class

    ::

        from polaris.network.network import Network

        net = Network()
        net.open('D:/Argonne/GTFS/CHICAGO/chicago2018-Supply.sqlite')

        curr = net.conn.cursor()
        curr.execute('SELECT node FROM Node order by node')


        for node in nodes:
            intersection = net.get_intersection(node)

            # To rebuild the intersection checking OSM, one can just do this
            intersection.rebuild_intersection(check_type='osm'):

            # Or one can do each step to be able to manipulate the signal as they go
            intersection.rebuild_connections()
            if intersection.osm_signal():
            # if intersection.determine_geometric_need_for_signal()
                if not intersection.supports_signal():
                    print(f'Node {node} does not support a signal. Skipping it')
                    continue
                sig = intersection.create_signal()
                # Here you can manipulate the signal
                sig.re_compute()
                # Or after recomputing as well
                sig.save()
    """

    def __init__(
        self,
        data_tables,
        path_to_file: PathLike,
        conn: Optional[sqlite3.Connection] = None,
        osm: Optional[OSM] = None,
        driving_side=None,
    ):
        self.u_turn = False
        self.node = -1
        self._data = data_tables
        self.incoming = []  # type: List[Approximation]
        self.outgoing = []  # type: List[Approximation]
        self.overrides = []  # type: List[tuple]

        self.__osm = osm or OSM(path_to_file)

        self.__osm_has_it: Optional[bool] = None
        self.__exists = True
        self.__bulk_loading__ = False
        self.intersection_type = "disconnected"
        self.url = UserConfig().osm_url
        self._connection_data = pd.DataFrame([])

        self.periods = [["0:00", "24:00"]]
        self.geo = Point()  # type: Point
        self.zone = -1
        self.__area_type = -1
        self._path_to_file = path_to_file
        with conn or read_and_close(self._path_to_file, spatial=True) as conn:
            self.__get_parameters(conn)
            self.srid = get_srid(conn=conn)
            self.driving_side = driving_side or get_driving_side(conn=conn)

    def load(self, node: int, conn: Optional[sqlite3.Connection] = None) -> None:
        """Loads the intersection object for the provided node

        Args:
            *node* (:obj:`int`): Node ID to load as an intersection
        """
        self.node = int(node)
        with conn or read_and_close(self._path_to_file, spatial=True) as conn:
            dt = conn.execute("SELECT zone, ST_AsBinary(geo) from Node where node=?", [self.node]).fetchone()
            if dt is None:
                self.__exists = False
            else:
                self.__exists = True
                self.zone, geo = dt
                self.geo = shapely.wkb.loads(geo)

                # We collect all required information from the node/intersection
                self.__connection_inventory(conn)
            if len(self.incoming + self.outgoing) < 1:
                self.__exists = False
                return

    def allow_pockets_for_all(self) -> None:
        """Allows all approximations for this intersection to have pockets created for them

        Default permissions for pocket creation are extracted from the Link_Type table.
        For more information go to the table documentation"""

        for approx in self.incoming:  # type: Approximation
            approx.set_allow_pockets()
        for approx in self.outgoing:
            approx.set_allow_pockets()

    def block_pockets_for_all(self) -> None:
        """Blocks all approximations for this intersection to have pockets created for them

        Default permissions for pocket creation are extracted from the Link_Type table.
        For more information go to the table documentation"""

        for approx in self.incoming:
            approx.set_block_pockets()
        for approx in self.outgoing:
            approx.set_block_pockets()

    def rebuild_intersection(self, conn: sqlite3.Connection, signal_type="keep_existing", clear_it_first=True):
        """Rebuilds an entire intersection

        Removes connections and traffic signals before rebuilding connections and (optionally) signals

        Args:
            *signal_type* (:obj:`str`, **Optional**): Type of check to determine if a signal should be added.
            Defaults to keeping existing intersection control type

        *check_type*
            * 'geometric': Determines need for signal based on the intersection geometry
            * 'osm': Determines need for signal based on the existence of such on OSM
            * 'forced': Forces the placement of a signal
            * 'stop_sign': Places stop signs in the intersection only
            * 'none': Does not place any type of intersection control on this intersection
            * 'keep_existing': Keeps the intersection control currently in place for the intersection
        """
        ct = signal_type.lower()
        if ct not in ["geometric", "osm", "forced", "stop_sign", "none", "keep_existing"]:
            raise ValueError("Wrong value for check_type")

        if ct == "keep_existing":
            ct = "forced" if self.has_signal(conn) else ct
            ct = "stop_sign" if self.has_stop_sign(conn) else ct

        if not self.__exists:
            return

        self.__connection_rebuilding(clear_it_first, conn)

        add_signal = False
        if ct == "geometric":
            add_signal = self.determine_geometric_need_for_signal(conn)
        elif ct == "osm":
            add_signal = self.osm_signal()
        elif ct == "forced":
            add_signal = True

        if add_signal and self.supports_signal(conn):
            self.create_signal(conn)
        elif ct == "stop_sign":
            st = StopSign(self)
            st.re_compute()
            st.save(conn)

    def add_stop_sign(self, conn: sqlite3.Connection):
        """Adds a stop sign to this intersection"""

        self.delete_signal(conn)
        self.delete_stop_sign(conn)

        st = StopSign(self)
        st.re_compute()
        st.save(conn)

    def rebuild_connections(self, clear_it_first=True, conn: Optional[sqlite3.Connection] = None) -> None:
        """Rebuilds all connections for the intersection

        Removes any pre-existing connections and traffic signal for this intersection

        Args:
            *clear_it_first* (:obj:`bool`, **Optional**): Whether to clear existing connections, pockets and signals
            It allows faster processing if no prior clearing is needed, but it will fail if connections and pockets
            data still exist for this node. Defaults to True
        """
        if not self.__exists:
            return
        with conn or read_and_close(self._path_to_file, spatial=True) as conn:
            self.__connection_rebuilding(clear_it_first, conn)

        logger.info(f"Rebuilt connections for node {self.node}")
        if self.__bulk_loading__:
            return

        self._data.refresh_cache("Connection")

    def __connection_rebuilding(self, clear_it_first: bool, conn: sqlite3.Connection):
        self.__get_parameters(conn)
        if clear_it_first:
            self.delete_stop_sign(conn)
            if self.has_signal(conn):
                self.delete_signal(conn)
            self.__clear_connections(conn)
        data = self._creates_connections(conn)
        if data.empty:
            raise ValueError("Node is not connected to any links")
        dt = data[[x for x in data.columns if str(x).lower() != "geo"]]
        dt.to_sql("Connection", conn, if_exists="append", index=False)
        geos = data[["geo", "link", "to_link"]].assign(srid=int(self.srid))
        geos["geo"] = gpd.GeoSeries(geos.geo).to_wkb()
        geos_array = geos[["geo", "srid", "link", "to_link"]].to_records(index=False)
        conn.executemany("Update Connection set Geo=GeomFromWKB(?,?) where link=? and to_link=?", geos_array)
        conn.commit()
        # conn.executemany(connections[0].insert_sql, data)
        self.save_pockets(conn)
        conn.commit()

    def block_movement(self, from_link: int, to_link: int, conn: sqlite3.Connection) -> None:
        """Blocks a movement by inserting it in the Turn_Overrides table with a penalty of -1

        It also recomputes the signal in the intersection in case there is a signal to be re-computed

        Args:
            *from_link* (:obj:`int`): Origin link for the allowed turn
            *to_link* (:obj:`int`): Destination link for the allowed turn
        """
        incs = [approx for approx in self.incoming if approx.link == from_link]
        outs = [approx for approx in self.outgoing if approx.link == to_link]

        if len(incs + outs) < 2:
            logger.error(f"Connection {from_link}-{to_link} is already not possible")
            return

        inc = incs[0]  # type:Approximation
        out = outs[0]  # type:Approximation

        # Adds the constraint
        sql = "select count(*) from Turn_Overrides where link=? and to_link=?"
        if conn.execute(sql, [from_link, to_link]).fetchone()[0] == 0:
            sql = "Insert into Turn_Overrides(link, dir, to_link, to_dir, node, penalty) Values(?, ?, ?, ?, ?, -1)"
            conn.execute(sql, [from_link, inc.direction, to_link, out.direction, self.node])
        else:
            conn.execute("UPDATE Turn_Overrides set penalty=-1 where link=? and to_link=?", [from_link, to_link])

        # Removes from the connection table
        conn.execute("DELETE FROM Connection where link=? and to_link=?", [from_link, to_link])
        conn.commit()

        if self.has_signal(conn):
            self.delete_signal(conn)
            self.create_signal(conn)
            self.__refresh_tables()

        conn.commit()
        self.load(self.node, conn)

    def add_movement(self, from_link: int, to_link: int, conn: sqlite3.Connection, note="") -> None:
        """
        Allows a movement by inserting it in the Turn_Overrides table with a penalty of 0

        Args:
            *from_link* (:obj:`int`): Origin link for the allowed turn
            *to_link* (:obj:`int`): Destination link for the allowed turn
            *note* (:obj:`str`): Any notes that should be added to the Turn_Overrides table
        """
        incs = [approx for approx in self.incoming if approx.link == from_link]
        outs = [approx for approx in self.outgoing if approx.link == to_link]

        if len(incs + outs) < 2:
            logger.error(f"Connection {from_link}-{to_link} is not possible")
            return

        inc = incs[0]  # type:Approximation
        out = outs[0]  # type:Approximation

        # Deletes any previously existing constraints
        conn.execute("DELETE FROM Turn_Overrides where link=? and to_link=?", [from_link, to_link])

        # Adds the constraint
        sql = "Insert into Turn_Overrides(link, dir, to_link, to_dir, node, penalty, notes) Values(?, ?, ?, ?, ?, 0, ?)"
        conn.execute(sql, [from_link, inc.direction, to_link, out.direction, self.node, note])
        conn.commit()
        self.rebuild_connections(True, conn)

        if self.has_signal(conn):
            self.delete_signal(conn)
            self.create_signal(conn)
            self.__refresh_tables()

        self.load(self.node, conn)

    def osm_signal(self, buffer=30, re_check=False, return_when_fail=False) -> bool:
        """We check Open-Streets Map for a traffic light in this vicinity

        Before making the first call to this function, it is recommended
        deploying your own OSM Overpass server and set IP and sleep time
        appropriately. See the OSM module documentation for more details


        Args:
            *buffer* (:obj:`int`, **Optional**): Distance between node and OSM signal to be considered same point.
            Defaults to 30m

            *re_check* (:obj:`bool`, **Optional**): To check again for a different buffer, set it to True.
            Defaults to False

            *return_when_fail* (:obj:`bool`, **Optional**): Value to return when the OSM query fails.

        ::

                # Here we default to our own server
                osm = net.osm
                osm.url = 'http://192.168.0.105:12345/api'
                osm.sleep_time = 0

        """

        if not self.__exists:
            return False

        if self.__osm_has_it is None or re_check:
            closest_traffic_light = self.__osm.get_traffic_signal(self.geo)

            if closest_traffic_light is None:
                self.__osm_has_it = False
            elif closest_traffic_light.distance > buffer:
                self.__osm_has_it = False
            else:
                self.__osm_has_it = True

        return return_when_fail if self.__osm.failed else self.__osm_has_it

    def has_signal(self, conn: sqlite3.Connection) -> bool:
        """Checks if there is a signal for this intersection"""
        if not self.__exists:
            return False
        return sum([x[0] for x in conn.execute("select count(*) from Signal where nodes=?", [self.node])]) > 0

    def has_stop_sign(self, conn: sqlite3.Connection) -> bool:
        """Checks if there is a signal for this intersection"""
        if not self.__exists:
            return False
        return sum([x[0] for x in conn.execute("select count(*) from Sign where nodes=?", [self.node])]) > 0

    def delete_stop_sign(self, conn: sqlite3.Connection):
        """Deletes the signal for this intersection"""

        if not self.__exists:
            return

        logger.debug(f"Deleted stop sign for node {self.node}")
        # Deletes from the signal tables
        conn.execute("DELETE from Sign where nodes=?", [self.node])
        conn.commit()

    def delete_signal(self, conn: sqlite3.Connection):
        """Deletes the signal for this intersection"""

        if not self.__exists:
            return

        if not self.has_signal(conn):
            return

        logger.info(f"Deleted signal for node {self.node}")

        # Deletes from the signal tables
        signal_id = conn.execute("select signal from Signal where nodes=?", [self.node]).fetchone()[0]
        conn.execute("DELETE from Signal where nodes=?", [self.node])
        conn.execute("DELETE from Signal_Nested_Records where object_id=?", [self.node])

        # Deletes from the timing tables
        sql = "select timing_id from Timing where signal=?"
        timing_id = ",".join([str(x[0]) for x in conn.execute(sql, [signal_id]).fetchall()])
        conn.execute("DELETE from Timing where signal=?", [signal_id])
        sql = f"DELETE from Timing_Nested_Records where object_id IN ({timing_id})"
        conn.execute(sql)

        # Deletes from the phasing tables
        sql = "select phasing_id from Phasing where signal=?"
        phasing_id = ",".join([str(x[0]) for x in conn.execute(sql, [signal_id]).fetchall()])
        conn.execute("DELETE from Phasing where signal=?", [signal_id])
        conn.execute(f"DELETE from Phasing_Nested_Records where object_id IN ({phasing_id})")
        conn.commit()
        self.__refresh_tables()

    def create_signal(self, conn: sqlite3.Connection, compute_and_save=True) -> Optional[Signal]:
        """
        Returns a traffic signal object for this intersection

        Return:
            *signal* (:obj:`Signal`): Traffic signal object
        """
        if len(self.incoming) < 2:
            warn("Intersection only has one incoming link. No traffic signal possible")
            return None
        sig = Signal(self, conn)
        if not compute_and_save:
            return sig

        sig.re_compute(conn)
        self.delete_stop_sign(conn)
        sig.save(conn)
        return None

    def supports_signal(self, conn: sqlite3.Connection) -> bool:
        """If this intersection geometrically supports a signal (does it make sense)

        Return:
            *support* (:obj:`True`): Boolean for it a signal can be configured for this intersection"""

        if len(self.incoming) < 2 or len(self.outgoing) == 0:
            return False

        inc = sorted(self.connections(conn).link.unique())
        out = sorted(self.connections(conn).to_link.unique())
        if len(list(inc)) == len(list(out)) == 2 and inc == out:
            return False

        return True

    def determine_geometric_need_for_signal(self, conn: sqlite3.Connection) -> bool:
        """Determines if a signal is needed based on intersection geometry, link types and area type

        It is somewhat similar to the capability from TranSims"""

        # Steps for determining if we need an intersection
        if not self.__exists:
            return False

        return geom_need_for_signal(self, conn)

    def allowed_turns(self) -> List[List[int]]:
        """Returns a list of all link pairs allowed for convergence in this node"""
        should_have_pairs = []
        for inc in self.incoming:
            for out in self.outgoing:
                if should_allow(self, inc, out):
                    should_have_pairs.append([inc.link, out.link])
        return should_have_pairs

    def __connection_inventory(self, conn: sqlite3.Connection):
        data = [self.node, self.node, self.node, self.node]
        sql = """SELECT ? node, link, lanes_ab, ST_AsBinary(geo), lt.rank, lt.turn_pockets, 0 direc, 'incoming', bearing_b + 180 FROM Link l
                                                              INNER JOIN link_type lt on l.type=lt.link_type
                 where l.lanes_ab>0 and l.node_b=? AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                 lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')
                 UNION ALL
                 SELECT ? node, link, lanes_ba, ST_AsBinary(ST_Reverse(geo)), lt.rank, lt.turn_pockets, 1 direc, 'incoming', bearing_a FROM Link l
                                                                    INNER JOIN link_type lt on l.type=lt.link_type
                 where l.lanes_ba>0 and l.node_a=? AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                 lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')"""

        self.incoming = [Approximation(item, self.driving_side) for item in conn.execute(sql, data).fetchall()]

        sql = """SELECT ? node, link, lanes_ab, ST_AsBinary(geo), lt.rank, lt.turn_pockets, 0 direc, 'outgoing', bearing_a + 180 FROM Link l
                                                              INNER JOIN link_type lt on l.type=lt.link_type
                 where l.lanes_ab>0 and l.node_a=? AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                 lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')
                 UNION ALL
                 SELECT ? node, link, lanes_ba, ST_AsBinary(ST_Reverse(geo)), lt.rank, lt.turn_pockets, 1 direc, 'outgoing', bearing_b FROM Link l
                                                                    INNER JOIN link_type lt on l.type=lt.link_type
                 where l.lanes_ba>0 and l.node_b=? AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                 lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')
                 """
        self.outgoing = [Approximation(item, self.driving_side) for item in conn.execute(sql, data).fetchall()]
        lengths = [len(self.incoming), len(self.outgoing)]
        if max(lengths) == 0:
            self.intersection_type = "disconnected"
            return

        self.incoming, self.outgoing = sort_approx_list(self.incoming + self.outgoing)
        # We check if they are put in the order we would like

        # We check if it is a dead-end to allow for UTURN
        if len(self.outgoing) == 1:
            self.u_turn = True

        # We check if this is the case of many to one or one-to-many
        ranks = set([inc.link_rank for inc in self.incoming] + [out.link_rank for out in self.outgoing])
        downstream_lanes = sum([x.lanes for x in self.outgoing])
        upstream_lanes = sum([x.lanes for x in self.incoming])
        if lengths == [1, 0] or upstream_lanes == 0:
            self.intersection_type = "Dead-end"
        elif lengths == [0, 1] or downstream_lanes == 0:
            self.intersection_type = "Dead-start"
        elif lengths == [1, 1]:
            self.intersection_type = "top_to_top"
        elif all(r in [RAMP, FREEWAY, EXPRESSWAY] for r in ranks):
            self.intersection_type = "freeway"
        elif min(lengths) == 1 and max(lengths) > 1:
            self.intersection_type = "merge"
        else:
            self.intersection_type = "generic"

    def _creates_connections(self, conn: sqlite3.Connection) -> pd.DataFrame:
        if self.intersection_type == "disconnected":
            raise Exception(f"Node {self.node} is completely disconnected")
        if self.intersection_type in ["Dead-end", "Dead-start"]:
            return pd.DataFrame([[np.nan] * len(conn_table_fields)], columns=conn_table_fields).dropna()
        # If this is a dead end (or any other case where only one movement is possible)
        elif self.intersection_type == "top_to_top":
            connec = connect_two_links_top_to_top(self.incoming[0], self.outgoing[0])
            return pd.DataFrame([connec.data], columns=conn_table_fields)
        # If this is a freeway intersection
        elif self.intersection_type == "freeway":
            connections = FreewayIntersection(self).build(conn)
        # This is a simple link merge, where there is no much option to fix this
        elif self.intersection_type == "merge":
            connections = LinksMerge(self).build(conn)
        else:
            connections = GenericIntersection(self).build(conn)  # Seems to handle driving side

        if len(connections) == 0:
            # We add some forced connectivity to ensure the node is connected
            logging.info(f"Connectivity for Node {self.node} was forced. You should inspect it on a map")
            connections = [ConnectionRecord(inc, self.outgoing[0]) for inc in self.incoming]

        self._connection_data = pd.DataFrame([x.data for x in connections], columns=connections[0].database_fields)
        return self._connection_data

    @property
    def connection_data_records(self):
        if self._connection_data.empty:
            df = self._data["Connection"]
            return df.loc[df.node == self.node, :]
        return self._connection_data

    @property
    def _builds_pockets(self) -> pd.DataFrame:
        dt = [street.pocket_data for street in self.incoming + self.outgoing if street.has_pockets]
        return pd.concat(dt) if dt else pd.DataFrame()

    def save_pockets(self, conn: sqlite3.Connection):
        dt = self._builds_pockets
        if not dt.empty:
            dt.to_sql("Pocket", conn, if_exists="append", index=False)

    def __clear_connections(self, conn: sqlite3.Connection):
        conn.execute("DELETE from Connection where node=?", [self.node])

        conn.execute("DELETE from Sign where nodes=?", [self.node])

        # We also clear all the associated pockets
        dt = [[inc.link, inc.direction] for inc in self.incoming]
        conn.executemany('Delete from Pocket where link=? and dir=? and type not like "%MERGE"', dt)

        dt = [[out.link, out.direction] for out in self.outgoing]
        conn.executemany('Delete from Pocket where link=? and dir=? and type like "%MERGE"', dt)
        conn.commit()

    def __get_parameters(self, conn: sqlite3.Connection):
        sql = 'Select infovalue from About_Model where infoname="U-TURN allowed"'
        u_turn = conn.execute(sql).fetchone()
        if u_turn:
            self.u_turn = eval(u_turn[0].title())

        sql = "Select link, to_link, penalty from Turn_Overrides where node=?"
        self.overrides = list(conn.execute(sql, [self.node]).fetchall())

    def connections(self, conn: Optional[sqlite3.Connection] = None):
        if self._connection_data.empty:
            with conn or read_and_close(self._path_to_file, spatial=True) as conn:
                fields, _, geo_field = find_table_fields(conn, "Connection")
                fields = [f"{x}" for x in fields]
                if geo_field is not None:
                    fields.append("ST_AsBinary(geo) geo")
                fields.append(
                    "round(Degrees(ST_Azimuth(StartPoint(geo), ST_PointN(SanitizeGeometry(geo), 2))),0) bearing"
                )
                fields.append("link || '-' || to_link key ")
                keys = ",".join(fields)
                self._connection_data = pd.read_sql_query(f"select {keys} from Connection where node={self.node}", conn)
            fltr = self._connection_data.geo.isna()
            self._connection_data.loc[~fltr, "geo"] = self._connection_data.geo[~fltr].apply(shapely.wkb.loads)
        return self._connection_data

    def links(self, conn: sqlite3.Connection):
        sql = f"""select l.link link, 1 direction, lt.rank link_rank,
                          round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(l.geo), 2),StartPoint(l.geo) )),0) bearing
                        from Link l inner join Link_type lt on lt.link_type=l.type where node_a={self.node}  and l.lanes_ba > 0
                        union ALL
                       select l.link link, 0 direction, lt.rank link_rank,
                       round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(l.geo), ST_NumPoints(SanitizeGeometry(l.geo))-1), EndPoint(l.geo))),0) bearing
                       from Link l inner join Link_type lt on lt.link_type=l.type where node_b={self.node} and l.lanes_ab > 0"""

        df = pd.read_sql_query(sql, conn).sort_values("bearing")
        df = df.assign(direction="")
        df.direction = df.bearing.apply(find_directions)
        return df

    def __refresh_tables(self):
        for tn in [
            "Timing",
            "Timing_Nested_Records",
            "Phasing",
            "Phasing_Nested_Records",
            "Signal",
            "Signal_nested_Records",
        ]:
            self._data.refresh_cache(tn)
