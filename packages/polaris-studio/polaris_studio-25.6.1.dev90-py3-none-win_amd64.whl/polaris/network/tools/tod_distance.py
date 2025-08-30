# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import read_and_close


class DistanceToTransit:
    def __init__(self, path_to_file: os.PathLike):
        from aequilibrae.paths import Graph

        self._path_to_file = Path(path_to_file)
        self.criteria = None
        self.__brt_nodes = np.zeros([])
        self.__rail_nodes = np.zeros([])
        self._tw = pd.DataFrame([])
        self._loc = pd.DataFrame([])
        self._all_stops = pd.DataFrame([])
        self._tod_stops = np.array([], dtype=np.int64)
        self._node_corresp = pd.DataFrame([])

        self._graph = Graph()
        self._load_data()

    def locations_within_distance(
        self, distance: float, stops: Optional[list] = None, use_routed_distance=True
    ) -> list:
        if stops is not None:
            self.set_tod_stops(tod_stops=np.array(stops, np.int64))

        if use_routed_distance:
            results = self.build_tod_distances()
        else:
            results = self.euclidean_distances()
        return results[results.distance_to_tod <= distance].location.tolist()

    def build_tod_distances(self):
        from aequilibrae.paths import PathResults

        ts = self._tod_stops
        if ts.shape[0] == 0:
            raise ValueError("No TOD stops have been set")

        tod_nodes = self._node_corresp.query("supply_node in @ts")

        locs = np.array(sorted(self._loc.location.tolist()), np.int64)

        min_dist = np.empty(locs.shape[0], np.float64)
        min_dist.fill(np.inf)

        res = PathResults()
        res.prepare(self._graph)
        for _, rec in tod_nodes.iterrows():
            tod_node = rec.node
            res.compute_path(tod_node, locs[0])
            dist = res.skims[locs][:, 0]
            min_dist = np.minimum(min_dist, dist)

            if min_dist.min() < 1:
                closest_loc = int(np.where(dist == dist.min())[0][0])
                print(rec.supply_node, closest_loc)
                res.update_trace(int(closest_loc))

        return pd.DataFrame({"location": locs, "distance_to_tod": min_dist})

        # Parallelized over locations
        # This may become relevant if the number of stops of interest is too large

        # Let's divide the list of locations in chunks of 30,000 locations
        # csize = 30000
        # locs = [locs[i:i + csize] for i in range(0, len(locs), csize)]
        # for set_locs in locs:
        #     centroids = np.hstack([np.array(set_locs, np.int64), tod_graph_nodes])
        #     self._graph.prepare_graph(centroids)
        #     ns = NetworkSkimming(self._graph)
        #     ns.execute()

    def euclidean_distances(self):
        ts = self._tod_stops
        if ts.shape[0] == 0:
            raise ValueError("No TOD stops have been set")

        tod_nodes = self._all_stops.query("stop_id in @ts")

        return self._loc.sjoin_nearest(tod_nodes, distance_col="distance_to_tod")[["location", "distance_to_tod"]]

    def set_tod_stops(self, tod_stops: np.ndarray = None, get_rail=True, get_brt=True):  # type: ignore
        tod_stops = tod_stops if tod_stops is not None else np.array([], dtype=np.int64)
        if get_rail:
            tod_stops = np.hstack([tod_stops, self.rail_nodes])
        if get_brt:
            tod_stops = np.hstack([tod_stops, self.brt_nodes])
        self._tod_stops = tod_stops

    @property
    def brt_nodes(self) -> np.ndarray:
        if sum(self.__brt_nodes.shape) == 0:
            sql = """SELECT distinct(FROM_node) brt_stops FROM Transit_Links WHERE pattern_id IN (
                        SELECT pattern_id FROM Transit_Patterns WHERE route_id in (
                            SELECT route_id FROM Transit_Routes WHERE shortname LIKE "%BRT%" or longname LIKE "%BRT%"))
                     UNION ALL
                     SELECT distinct(to_node) brt_stops FROM Transit_Links WHERE pattern_id IN (
                        SELECT pattern_id FROM Transit_Patterns WHERE route_id in (
                            SELECT route_id FROM Transit_Routes WHERE shortname LIKE "%BRT%" or longname LIKE "%BRT%"))
            """
            with read_and_close(self._path_to_file) as conn:
                self.__brt_nodes = pd.read_sql(sql, conn).drop_duplicates().brt_stops.to_numpy()

        return self.__brt_nodes

    @property
    def rail_nodes(self) -> np.ndarray:
        if sum(self.__rail_nodes.shape) == 0:
            sql = "select stop_id rail_stops from Transit_Stops where route_type in (0, 1, 2, 5)"
            with read_and_close(self._path_to_file) as conn:
                self.__rail_nodes = pd.read_sql(sql, conn).drop_duplicates().rail_stops.to_numpy()
        return self.__rail_nodes

    def _build_graph(self):
        from aequilibrae.paths import Graph

        max_loc = self._loc.location.max() + 2
        all_nodes = np.sort(np.unique(np.hstack([self._tw.from_node.to_numpy(), self._tw.to_node.to_numpy()])))
        self._node_corresp = pd.DataFrame({"node": np.arange(all_nodes.shape[0]) + max_loc, "supply_node": all_nodes})

        # We adapt the nodes we are interested in
        trans1 = {"supply_node": "from_node", "node": "a_node"}
        trans2 = {"supply_node": "to_node", "node": "b_node"}
        net = self._tw.merge(self._node_corresp.rename(columns=trans1), on="from_node")
        net = net.merge(self._node_corresp.rename(columns=trans2), on="to_node")

        # We connect each location to the two nodes of its transit_walk link
        # We will add the distance to the walk link to make sure we consider the whole distance
        # That is currently missing from the location table

        connectors = self._loc[["location", "walk_link", "walk_offset", "geo"]]
        net_data = net[["walk_link", "a_node", "b_node", "length", "geo"]].rename_geometry("geo_net")
        connectors = connectors.merge(net_data, on="walk_link")
        connectors = connectors.assign(distance=connectors.geo.distance(connectors.geo_net))
        connectors = connectors.drop(columns=["geo", "geo_net"])

        conn1 = connectors[["location", "a_node", "distance", "walk_offset"]]
        conn1 = conn1.assign(distance=conn1.distance + connectors.walk_offset)
        conn1 = conn1.rename(columns={"location": "a_node", "a_node": "b_node"})
        conn1 = conn1.drop(columns=["walk_offset"])

        conn2 = connectors[["location", "b_node", "length", "walk_offset", "distance"]]
        conn2 = conn2.assign(distance=conn1.distance + conn2["length"] - conn2.walk_offset)
        conn2 = conn2.drop(columns=["walk_offset", "length"]).rename(columns={"location": "a_node"})

        connectors = pd.concat([conn1, conn2])

        # The distance of the two connectors combined will 0.1m larger than the link to avoid short-circuiting
        connectors.distance += 0.1
        connectors = connectors.assign(link_id=np.arange(connectors.shape[0]) + net.walk_link.max() + 2)

        # We add the connectors to the network
        net = net.rename(columns={"length": "distance", "walk_link": "link_id"})
        net = pd.concat([connectors, net[["a_node", "b_node", "distance", "link_id"]]])
        net = net.assign(direction=0)

        # For debugging purposes, we can comment this line below
        net.link_id = np.arange(net.shape[0]) + 1

        # And build the AequilibraE graph
        graph = Graph()
        graph.network = net
        graph.prepare_graph(self._loc.location.to_numpy())
        graph.set_graph(cost_field="distance")
        graph.set_blocked_centroid_flows(False)
        graph.set_skimming(["distance"])
        return graph

    def _load_data(self):
        with read_and_close(self._path_to_file, spatial=True) as conn:
            dtc = DataTableAccess(self._path_to_file)
            srid = get_srid(self._path_to_file)
            self._tw = dtc.get("Transit_Walk", conn=conn).to_crs(srid)
            self._loc = dtc.get("Location", conn=conn).to_crs(srid)
            self._all_stops = dtc.get("Transit_Stops").query("route_type>=0").to_crs(srid)

        self._graph = self._build_graph()
