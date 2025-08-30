# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import multiprocessing as mp
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from aequilibrae.paths.graph import Graph

from polaris.utils.database.data_table_access import DataTableAccess


class StaticGraph:
    def __init__(self, supply_pth: Path, enforce_connectivity=True):
        self.supply_pth = supply_pth
        self._graph = Graph()
        self.node_offset = 0

        self.links = DataTableAccess(self.supply_pth).get("Link")
        self.nodes = DataTableAccess(self.supply_pth).get("Node").drop(columns=["zone"])
        self.zones = DataTableAccess(self.supply_pth).get("Zone")
        self.enforce_connectivity = enforce_connectivity
        self._disconnected_nodes = []

    def build_graph(self):
        # Make sure it is all in the same CRS, in case it was changed at some point
        self.__basic_graph_build()
        if self.enforce_connectivity:
            while self.__find_disconnected():
                logging.critical("Graph centroid has been connected to a disconnected node. Trying to fix it")
                self.__basic_graph_build()

    def __basic_graph_build(self):
        self.nodes = self.nodes.to_crs(self.links.crs)
        if not self.zones.empty:
            self.zones = self.zones.to_crs(self.links.crs)
            self.node_offset = self.zones.zone.max() + 1

        ltype = DataTableAccess(self.supply_pth).get("Link_type").reset_index()[["link_type", "use_codes"]]
        links = self.links.merge(ltype, left_on="type", right_on="link_type")

        # Filter links
        links = links[
            links.use_codes.str.lower().str.contains("auto") | links.use_codes.str.lower().str.contains("truck")
        ]

        # Let's assert some things about the links so we can get everything we need for a static traffic assignment
        # First, capacities
        links = links.assign(capacity_ab=0, capacity_ba=0)
        capacity_dict = {"MAJOR": 750, "RAMP": 800, "PRINCIPAL": 800, "FREEWAY": 1200, "EXPRESSWAY": 1200}
        capacity_dict = capacity_dict | {"FRONTAGE": 600, "BRIDGE": 600, "TUNNEL": 600, "EXTERNAL": 600, "OTHER": 600}
        capacity_dict = capacity_dict | {"LOCAL": 300, "LOCAL_THRU": 350, "COLLECTOR": 400, "MINOR": 600}

        for ltype, lanecap in capacity_dict.items():
            for capfield, lanesfield in [("capacity_ab", "lanes_ab"), ("capacity_ba", "lanes_ba")]:
                links.loc[links["type"].str.upper() == ltype, capfield] = (
                    links.loc[links["type"].str.upper() == ltype, lanesfield] * lanecap
                )

        zero_cap = list(links.query("capacity_ab + capacity_ba ==0")["type"].unique())
        if len(zero_cap) > 0:
            warnings.warn(f"Link types {','.join(zero_cap)} have zero capacity")

        # Now free-flow travel times in minutes
        links = links.assign(
            time_ab=(links["length"] / links.fspd_ab) / 60, time_ba=(links["length"] / links.fspd_ba) / 60
        )
        links.replace([np.inf, -np.inf], 0, inplace=True)
        # Division can return infinite values, so let's fix them

        # Now, directions
        links = links.assign(direction=0, source="supply_file")
        links.loc[links.lanes_ab == 0, "direction"] = -1
        links.loc[links.lanes_ba == 0, "direction"] = 1
        links = links[links.lanes_ab + links.lanes_ba > 0]

        # Now we get only the columns we need
        lnks_net = links[
            [
                "link",
                "length",
                "node_a",
                "node_b",
                "capacity_ab",
                "capacity_ba",
                "time_ab",
                "time_ba",
                "direction",
            ]
        ]
        lnks_net = lnks_net.rename(
            columns={"link": "link_id", "node_a": "a_node_network", "node_b": "b_node_network", "length": "distance"}
        )

        lnks_net = lnks_net.assign(connector_penalty=0, a_node=lnks_net.a_node_network, b_node=lnks_net.b_node_network)

        # Polaris models do not have centroids and connectors, so we need to create them
        # Get nodes and zones
        if self.zones.empty:
            connectors = pd.DataFrame([])
            centroids = None
        else:
            # Let's shift the node IDs to make sure our zone numbers do not conflict with node IDs
            self.nodes.node += self.node_offset
            lnks_net.a_node += self.node_offset
            lnks_net.b_node += self.node_offset

            centroid = self.zones.geometry.centroid
            zones = gpd.GeoDataFrame(self.zones.zone, geometry=centroid, crs=self.zones.crs)

            # Only get the nodes that are actually in the network
            nodes = self.nodes[(self.nodes.node.isin(lnks_net.a_node)) | (self.nodes.node.isin(lnks_net.b_node))]
            nodes = nodes[~nodes.node.isin(self._disconnected_nodes)]
            connectors = zones.sjoin_nearest(nodes, how="left", distance_col="distance").sort_values(by=["distance"])
            connectors = connectors.drop_duplicates(subset="distance", keep="first")
            connectors = connectors[["node", "zone", "distance"]]

            missing_centroids = zones[~zones.zone.isin(connectors.zone)]
            if not missing_centroids.empty:
                # Makes sure that ALL centroids appear in the graph
                connectors2 = pd.DataFrame({"node": zones.zone, "zone": zones.zone, "distance": 0.001})
                connectors = pd.concat([connectors, connectors2], ignore_index=True)

            # Create connectors with speed of 12 m/s, or 43 km/h
            # This is to make sure that the connector to the closest node will be used, unless not actually connected
            connectors = connectors.assign(
                b_node_network=connectors["node"] - self.node_offset,
                direction=0,
                capacity_ab=1000000,
                capacity_ba=1000000,
                time_ab=connectors["distance"] / 12 / 60,
                time_ba=connectors["distance"] / 12 / 60,
                connector_penalty=connectors["distance"] * 20 + 0.001,
                source="centroid_connector",
            )
            connectors = connectors.assign(link_id=np.arange(connectors.shape[0]) + lnks_net.link_id.max() + 1)
            connectors = connectors.rename(columns={"zone": "a_node", "node": "b_node"})
            connectors.distance *= 2  # Compensates for the internal detour missed by using connectors
            centroids = zones.zone.to_numpy()

        lnks_net = pd.concat([lnks_net, connectors], ignore_index=True)

        self._graph = Graph()
        self._graph.network = lnks_net
        self._graph.prepare_graph(centroids=centroids)
        self._graph.set_graph("time")
        self._graph.set_skimming(["distance", "time"])
        self._graph.set_blocked_centroid_flows(True)

    def __find_disconnected(self):
        if self._graph.centroids.shape[0] == 0:
            return False
        skimmer = self._graph.compute_skims(mp.cpu_count())
        problematic = np.isinf(skimmer.results.skims.distance) + np.isnan(skimmer.results.skims.distance)
        if not np.any(problematic):
            return False

        cand1 = np.where(problematic.sum(axis=0))[0]
        cand2 = np.where(problematic.sum(axis=1))[0]
        candidates = cand1 if cand1.shape[0] < cand2.shape[0] else cand2

        for idx in candidates:
            zone_ = self._graph.centroids[idx]
            nodes = self._graph.network.query("a_node == @zone_").b_node_network.unique()
            self._disconnected_nodes.extend(list(nodes))

        return True

    @property
    def graph(self) -> Graph:
        if self._graph.num_zones <= 0:
            self.build_graph()

        return self._graph
