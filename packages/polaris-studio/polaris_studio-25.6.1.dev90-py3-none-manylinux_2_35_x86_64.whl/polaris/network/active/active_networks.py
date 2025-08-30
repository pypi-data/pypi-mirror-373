# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from datetime import date
from math import ceil
from time import perf_counter
from typing import List, Dict, Union, Tuple

import numpy as np
import pandas as pd
from shapely.geometry import LineString

import polaris.network
from polaris.network.active.walk_network_link import WalkLink, get_walk_links_qry
from polaris.network.active.walk_network_node import WalkNode, TRANSIT_STOPS_QRY, MICROMOBILITY_QRY
from polaris.network.constants import BIKE_LINK_RANGE, WALK_LINK_RANGE, WALK_AGENCY_ID
from polaris.network.constants import WALK_AGENCY_NAME
from polaris.network.create.triggers import create_network_triggers, delete_network_triggers
from polaris.network.starts_logging import logger
from polaris.network.tools.geo import Geo
from polaris.network.tools.geo_index import GeoIndex
from polaris.network.utils.srid import get_srid
from polaris.network.utils.updater import updater
from polaris.network.utils.worker_thread import WorkerThread
from polaris.utils.database.db_utils import has_table, commit_and_close
from polaris.utils.signals import SIGNAL


class ActiveNetworks(WorkerThread):
    """Walking & Biking network building class

    ::

        from polaris.network.network import Network
        net = Network()
        net.open(path/to/network)

        active_net = new.active

        # Limits the length of active links to a known value
        # Any link grater than this value will be divided into pieces of
        # equal length smaller than this limit
        active_net.set_max_link_dist(800)

        # We can re-build the entire active network
        active_net.build()

        # After rebuilding the network, it will automatically rebuild the
        # reference to active links in the Location and Parking Tables

        # To rebuild the association of active links for the Location
        # and Parking tables after manual edit of the active network
        # please look into the GeoConsistency submodule
    """

    activenet = SIGNAL(object)

    def __init__(self, geotool, data_tables) -> None:
        WorkerThread.__init__(self, None)

        self.agency_id = WALK_AGENCY_ID
        self.agency_name = WALK_AGENCY_NAME
        # meters. The amount of extra active allowed to avoid further breaking walking links
        self.max_walk_deviation = 10
        self.__geo_consistency = polaris.network.consistency.geo_consistency.GeoConsistency(geotool, data_tables)
        self.__do_update_associations__ = True

        # meters: The maximum separation between nodes for which a direct connection can be created
        self.direct_connection_length = 15
        # The minimum detour (in relative terms) through the network that requires the creation of a direct connection
        self.detour_for_direct_connection = 0.4

        self.srid = -1
        self.__do_osm = False
        self.geo: Geo = geotool
        self.line_idx = GeoIndex()
        self.node_idx = GeoIndex()
        self.link_list: Dict[int, WalkLink] = {}
        self.nodes_list: Dict[int, WalkNode] = {}
        self.all_stops: Dict[int, WalkNode] = {}
        self.node_lookup: Dict[int, int] = {}
        self.__new_links: List[WalkLink] = []
        self.__new_stops: List[WalkNode] = []
        self.__delete_links: List[int] = []

        self.connectors: Dict[int, int] = {}

        self.broken = 0
        self.__time = 0
        self.master_msg_txt = "Rebuilding Walk network"
        self.__mlid__ = WALK_LINK_RANGE  # Tracker for Link ID so we don't repeat them
        self.__max_link_dist = np.inf
        self._network_file = geotool._network_file
        self.srid = get_srid(self._network_file)

    def set_max_link_dist(self, max_dist: float):
        """Sets the maximum length an active link should have

        Args:
            *max_dist* (:obj:`float`): Maximum distance allowed for the link
        """
        self.__max_link_dist = max_dist

    def doWork(self):
        """Alias for build"""
        self.build()

    def build(self):
        """Builds the active network from scratch

        It also rebuilds the correlation between active links and the Location and Parking Tables
        """

        with commit_and_close(self._network_file, spatial=True) as conn:
            delete_network_triggers(conn)
            self.__time = perf_counter()

            self.activenet.emit(["start", "master", 11, self.master_msg_txt])

            self._initialize_table(conn)

            self._check_agency(conn)

            self._copy_links_from_road_network(conn)

            create_network_triggers(conn)

            self._read_links(conn)
            self._break_long_links()

            self._save_changes(conn)

            self._read_links(conn)
            self._read_stops(conn)
            excess_added = self._break_links_at_stops()

            self._save_changes(conn)
            if excess_added:
                msg = "     {} link breakings were not used in the end. {}"
                logger.info(msg.format(len(excess_added), ",".join(excess_added)))

            self._connect_overlapping_stops(conn)

            self.copy_to_bike(conn)
            if self.__do_update_associations__:
                self.update_bearing(conn)
                self.__update_associations(conn)
            self.finish()

    def set_osm_source(self, do_osm=False):
        """Allows user to get a walk network from the OSM network instead of the roadway network

        Args:
            *do_osm* (:obj:`Bool`): Boolean for whether we should get our active network from OSM instead road network
        """

        self.__do_osm = do_osm

    def __increment_bar(self, *args, **kwargs):
        self.activenet.emit(["update", "master", 1, self.master_msg_txt])

    def __update_associations(self, conn: sqlite3.Connection):
        """Rebuilds the association of active links with the Location and Parking Tables"""
        self.__geo_consistency.update_active_network_association()
        self.__rebuild(conn)
        conn.execute(
            "Update Location set bike_offset=walk_offset, bike_link=walk_link + ?", [BIKE_LINK_RANGE - WALK_LINK_RANGE]
        )
        conn.commit()

    @updater(__increment_bar)
    def _check_agency(self, conn: sqlite3.Connection):
        sql = f"Select agency from Transit_Agencies where agency='{self.agency_name}';"
        dt = conn.execute(sql).fetchone()
        if dt is None:
            today = date.today().strftime("%y-%m-%d")
            dt = [self.agency_id, self.agency_name, today, today, "Synthetic walking network"]
            sql = """INSERT into Transit_Agencies (agency_id, agency, feed_date, service_date, description)
                                            Values(?,?,?,?,?);"""
            conn.execute(sql, dt)
            conn.commit()

    @updater(__increment_bar)
    def _initialize_table(self, conn: sqlite3.Connection):
        logger.info("Clearing Transit_walk table and synthetic active nodes from Transit_Stops")
        logger.debug("Clearing Transit_walk")
        conn.execute("DELETE from Transit_Walk;")
        logger.debug("Clearing Transit_bike")
        conn.execute("DELETE from Transit_Bike;")

        logger.debug("Clearing Synthetic active nodes from Transit_Stops")
        conn.execute("DELETE from Transit_Stops where agency_id=?;", [WALK_AGENCY_ID])
        conn.commit()

    @updater(__increment_bar)
    def _copy_links_from_road_network(self, conn: sqlite3.Connection) -> None:
        logger.info("Copying links from road network")

        transfer_qry = """INSERT into Transit_Walk(walk_link, from_node, to_node, "length",ref_link, geo)
                          SELECT link + ?, Node_a, Node_b, "length", link, geo from Link
                          INNER JOIN Link_Type ON Link.type = Link_Type.link_type
                          WHERE INSTR(Link_Type.use_codes, 'WALK')>0"""

        if self.__do_osm:
            transfer_qry = """INSERT into Transit_Walk(walk_link, from_node, to_node, "length",ref_link, geo)
                              SELECT link_id + ?, Node_a, Node_b, distance, link_id, geo from OSM_Walk"""

        conn.execute(transfer_qry, [WALK_LINK_RANGE])
        conn.commit()
        self.__rebuild(conn)

        if self.__do_osm:
            sql_nodes = """select distinct(stop_id), X, Y, geo from
                                (select distinct(node_a) stop_id, X(StartPoint(geo)) X, Y(StartPoint(geo)) Y,
                                        StartPoint(geo) geo from OSM_Walk
                                        where node_a not in (select node from node)
                           UNION ALL
                                 select distinct(node_b) stop_id, X(EndPoint(geo)) X, Y(EndPoint(geo)) Y,
                                        EndPoint(geo) geo from OSM_Walk
                                        where node_b not in (select node from node)) order by stop_id"""

            df = pd.read_sql(sql_nodes, conn)
            df = df.assign(
                stop="OSM_node",
                agency_id=WALK_AGENCY_ID,
                name="OSM_node",
                description="OSM_node",
                zone=0,
                has_parking=0,
                route_type=-1,
                Z=0,
            )
            df = df[
                [
                    "stop_id",
                    "stop",
                    "agency_id",
                    "X",
                    "Y",
                    "Z",
                    "name",
                    "description",
                    "zone",
                    "has_parking",
                    "route_type",
                    "geo",
                ]
            ]
            df.to_sql("Transit_Stops", conn, if_exists="append", index=False)

    @updater(__increment_bar)
    def _read_links(self, conn: sqlite3.Connection) -> None:
        # We build the spatial index with the active links to find the closest to each node

        logger.info("   Reading walk links")
        self.link_list.clear()

        self.line_idx = GeoIndex()
        for record in list(conn.execute(get_walk_links_qry)):
            lnk = WalkLink(record)
            self.link_list[lnk.walk_link] = lnk
            self.line_idx.insert(feature_id=lnk.walk_link, geometry=lnk.geo)
        self.__mlid__ = conn.execute("Select max(walk_link) + 1000 from Transit_Walk").fetchone()[0]

    @updater(__increment_bar)
    def _read_stops(self, conn: sqlite3.Connection) -> None:
        logger.info("   Loading Transit stops and mobility nodes")

        # We build the spatial index with the Transit Stops
        cases = [
            ["micromobility", "Micromobility_Docks", MICROMOBILITY_QRY],
            ["transit", "Transit_stops", TRANSIT_STOPS_QRY],
        ]

        tot = 0
        for _, tbl, _ in cases:
            tot += sum([x[0] for x in conn.execute(f"Select count(*) from {tbl}")])

        master_counter = 0
        for mode, table_name, get_qry in cases:
            if not has_table(conn, table_name):
                continue
            dt = conn.execute(get_qry).fetchall()
            logger.info("       Reading stops/docks and projecting onto links")

            for counter, record in enumerate(dt):
                master_counter += 1
                node = WalkNode()
                node.connecting = mode
                node.populate(record)
                self.nodes_list[node.stop_id] = node
                self.node_idx.insert(feature_id=counter, geometry=node.geo)
                self.node_lookup[counter] = node.stop_id

                # Returns 50 links whose bounding boxes are closest to the links
                # This is a huge exaggeration, but the performance impact is small and it guarantees robustness
                nearest = list(self.line_idx.nearest(node.geo, 50))
                min_dist = 100000000000
                clink = None
                for x in nearest:
                    d = self.link_list[x].geo.distance(node.geo)
                    if d < min_dist:
                        min_dist = d
                        clink = x
                if clink is None:
                    logger.warning(
                        f"We could not find any Walk link close to {mode} stop {node.stop_id}. "
                        f"Stop will be disconnected"
                    )
                    continue
                self.link_list[clink].stops.append(node.stop_id)

        # We remove all the links that do not have any stops projected there
        # Not the most efficient to loop again, but no time is spent and it make it easier to
        # look at what is happening
        self.link_list = {i_d: link for i_d, link in self.link_list.items() if link.stops}

    @updater(__increment_bar)
    def _break_long_links(self):
        for link in self.link_list.values():
            if link.geo.length <= self.__max_link_dist:
                continue

            parts = ceil(link.geo.length / self.__max_link_dist)
            segment_distance = link.geo.length / parts

            new_nodes = []
            new_projections = []
            for nodes in range(parts - 1):
                proj = segment_distance * (nodes + 1)
                new_stop = WalkNode()
                new_stop.geo = link.geo.interpolate(proj)
                new_stop.zone = self.geo.get_geo_item("zone", new_stop.geo)
                new_nodes.append(new_stop)
                new_projections.append(proj)
            self.__add_nodes_split_link(new_projections, link, new_nodes)

    def _break_links_at_stops(self) -> list:
        from polaris.network.transit.transit_elements.stop import Stop

        msg_txt = "Breaking active links at stops"
        logger.info(msg_txt)

        excess_added = []
        for link_id, link in self.link_list.items():
            # If a single transit stop projects here, then it is quite mechanic

            # We move in a greedy way from the beginning of the link towards the end and break for a group of
            # stops any time that adding a new stop to that group would add make us violate the constraint

            # Euclidean distances for each point to its projection on the link

            euclidean = [link.geo.distance(self.nodes_list[x].geo) for x in link.stops]

            projections = []
            persistent_projections = {}
            for x in link.stops:
                val = link.geo.project(self.nodes_list[x].geo)
                projections.append(val)
                persistent_projections[x] = val

            stops_in_order = [link.stops[projections.index(val)] for val in sorted(projections)]
            euclidean = [euclidean[projections.index(val)] for val in sorted(projections)]
            projections = sorted(projections)

            # We will sweep it in order in a greedy fashion and create as many nodes as we need
            new_nodes = []
            while stops_in_order:
                i = 1
                for i in range(1, len(stops_in_order) + 1):
                    avg = sum(projections[:i]) / i
                    avg_geo = link.geo.interpolate(avg)
                    to_avg = [avg_geo.distance(self.nodes_list[x].geo) for x in stops_in_order[:i]]
                    diff = [x - y for x, y in zip(to_avg, euclidean[:i])]
                    if max(diff) > self.max_walk_deviation:
                        i -= 1
                        break

                avg_projection = sum(projections[:i]) / i
                new_stop = WalkNode()

                new_stop.geo = link.geo.interpolate(avg_projection)
                new_nodes.append(new_stop)
                projections = projections[i:]
                stops_in_order = stops_in_order[i:]
                euclidean = euclidean[i:]

            # we go over all new nodes again to correctly associate stops to them
            idx = GeoIndex()
            association: Dict[int, List[Union[WalkNode, Stop]]] = {}
            for i, new_stop in enumerate(new_nodes):
                idx.insert(feature_id=i, geometry=new_stop.geo)
                association[i] = []

            for node_id in link.stops:
                node = self.nodes_list[node_id]
                i = list(idx.nearest(node.geo, 1))[0]
                association[i].append(node)

            new_nodes = []
            new_projections = []

            for _, nodes in association.items():
                if not nodes:
                    excess_added.append(str(link_id))
                    continue
                # We recompute to make sure this is the average for all nodes associated with it
                item_projections = [persistent_projections[x.stop_id] for x in nodes]
                proj = round(sum(item_projections) / len(nodes), 6)
                new_stop = WalkNode()
                new_stop.geo = link.geo.interpolate(proj)
                if proj == 0:
                    logger.debug(f"       Connecting stop to the start of a link. ref link: {link.ref_link}")
                    new_stop.stop_id = link.node_a
                    self.all_stops[new_stop.stop_id] = new_stop
                elif round(proj, 6) >= round(link.geo.length, 6):
                    logger.debug(f"       Connecting stop to the end of a link. ref link: {link.ref_link}")
                    new_stop.stop_id = link.node_b
                    self.all_stops[new_stop.stop_id] = new_stop
                else:
                    new_stop.zone = self.geo.get_geo_item("zone", new_stop.geo)
                    new_nodes.append(new_stop)
                    new_projections.append(proj)
                ids = [node.stop_id for node in nodes]
                self.__add_stop_connectors(ids, new_stop)
            self.__add_nodes_split_link(new_projections, link, new_nodes)

        return excess_added

    @updater(__increment_bar)
    def _save_changes(self, conn: sqlite3.Connection):
        conn.executemany("DELETE from Transit_Walk where walk_link=?", [[x] for x in self.__delete_links])
        self.__delete_links.clear()
        conn.commit()

        for new_link in self.__new_links:
            new_link.save(conn, self.srid, False)
        self.__new_links.clear()

        for new_stop in self.__new_stops:
            new_stop.save(conn, self.srid, False)
        self.__new_stops.clear()
        conn.commit()

    @updater(__increment_bar)
    def _connect_overlapping_stops(self, conn: sqlite3.Connection):
        logger.info("   Building direct transfer links")
        candidate_pairs: Dict[Tuple[int, int], int] = {}

        for stop_id, stop in self.nodes_list.items():

            # We do not connect overlapping micro-mobility stops
            if stop.connecting == "micromobility":
                continue
            # Returns 200 stops closest to each stop
            # This is a huge exaggeration, but the performance impact is small and it guarantees robustness
            nearest = list(self.node_idx.nearest(stop.geo, 100))
            for i in nearest:
                if stop_id == self.node_lookup[i]:
                    continue
                two_nodes = [stop_id, self.node_lookup[i]]
                candidate_pairs[min(two_nodes), max(two_nodes)] = 0
        added = 0

        self.all_stops.update(self.nodes_list)

        for node1, node2 in candidate_pairs.keys():
            node_a = self.nodes_list[node1]
            node_b = self.nodes_list[int(node2)]
            crow_dist = node_a.geo.distance(node_b.geo)
            if crow_dist < self.direct_connection_length:
                on_net_a = self.connectors[node_a.stop_id]
                on_net_b = self.connectors[node_b.stop_id]
                add = False
                if on_net_a != on_net_b:
                    add = True
                else:
                    geo = self.all_stops[on_net_a].geo
                    net_dist = node_a.geo.distance(geo) + node_b.geo.distance(geo)
                    # Detour is long enough that we want to detour
                    if crow_dist * (1 + self.detour_for_direct_connection) < net_dist:
                        add = True
                if add:
                    nl = WalkLink([None])
                    nl.node_a = node_a.stop_id
                    nl.node_b = node_b.stop_id
                    nl.distance = crow_dist
                    nl.geo = LineString([node_a.geo, node_b.geo])
                    nl.walk_link = self.__mlid__
                    self.__mlid__ += 1
                    self.__new_links.append(nl)
                    added += 1
        conn.commit()
        logger.info(f"     {added:,} direct connections added between stops")
        conn.commit()

    def __add_nodes_split_link(self, distances: List[float], link: WalkLink, new_nodes: List[WalkNode]):
        index = sorted(distances)
        sorted_nodes = [new_nodes[distances.index(x)] for x in index]
        self.__delete_links.append(link.walk_link)
        p = 0.0
        for new_node, avg in zip(sorted_nodes, index):
            avg = round(avg, 6)
            if avg - p <= 0:
                raise Exception(f"Trying to break a link before its start. Check link: {link.ref_link}")
            elif avg - p >= round(link.geo.length, 6):
                raise Exception(f"Trying to break a link after its end. Check link: {link.ref_link}")
            else:
                self.all_stops[new_node.stop_id] = new_node
                self.__new_stops.append(new_node)
                part_a, link = link.split(avg - p, new_node.stop_id)
                part_a.walk_link = self.__mlid__
                self.__new_links.append(part_a)
                self.broken += 1
                self.__mlid__ += 1
            p = avg
        link.walk_link = self.__mlid__
        self.__mlid__ += 1

        self.__new_links.append(link)

    def __add_stop_connectors(self, node_list: List[int], new_node: WalkNode):
        for node_id in node_list:
            node = self.nodes_list[node_id]
            connector = WalkLink([self.__mlid__])
            connector.node_a = node.stop_id
            connector.node_b = new_node.stop_id
            connector.geo = LineString([node.geo, new_node.geo])
            self.__mlid__ += 1
            self.__new_links.append(connector)
            self.connectors[node.stop_id] = new_node.stop_id

    @updater(__increment_bar)
    def copy_to_bike(self, conn: sqlite3.Connection):
        """
        Copies all records from Transit_Walk table into the Transit_Bike one changing the range for links
        """
        df = pd.read_sql('SELECT from_node, to_node, "length", walk_link, ref_link, geo from Transit_Walk', conn)
        df.rename(columns={"walk_link": "bike_link"}, inplace=True)
        df["bike_link"] += BIKE_LINK_RANGE - WALK_LINK_RANGE
        df.to_sql("Transit_Bike", conn, if_exists="append", index=False)

    def __rebuild(self, conn: sqlite3.Connection):
        conn.execute('select RecoverSpatialIndex("Transit_Walk", "geo");')
        conn.execute('select RecoverSpatialIndex("Transit_Stops", "geo");')
        conn.commit()

    def __signal_handler(self, val):
        self.activenet.emit(val)

    def finish(self):
        """Kills the progress bar so others can be generated"""
        self.activenet.emit(["finished_walking_procedure"])

    @staticmethod
    def update_bearing(conn: sqlite3.Connection):
        def update_bearing(table_name):
            return f"""update {table_name}
                      set "bearing_a" = coalesce(round(Degrees(ST_Azimuth(StartPoint(geo),
                                                                 ST_PointN(SanitizeGeometry(geo), 2))),0), 0),
                      "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(geo),
                                                             ST_NumPoints(SanitizeGeometry(geo))-1),
                                                                          EndPoint(geo))),0), 0)"""

        for sql in [update_bearing(tn) for tn in ["Transit_Walk", "Transit_Bike"]]:
            conn.execute(sql)
        conn.commit()
