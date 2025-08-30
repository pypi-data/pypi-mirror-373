# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import Dict, List, Any

import networkx as nx
import pandas as pd

from polaris.network.utils.worker_thread import WorkerThread
from polaris.utils.database.db_utils import read_and_close
from polaris.utils.signals import SIGNAL


class Diagnostics(WorkerThread):
    """Network diagnostics

    ::

        # We open the network
        from polaris_network import Network
        n = Network()
        n.open(source)

        # We get the checker for this network
        diag = n.diagnostics


        # We get the links below a certain distance threshold
        diag.short_links(threshold=50)

        # We get the nodes that are part of links below a certain distance threshold
        diag.short_links(threshold=50, returns='nodes')
    """

    diagnostics = SIGNAL(object)

    def __init__(self, geotools, data_tables):
        WorkerThread.__init__(self, None)

        self.geotools = geotools  # type:polaris.network.tools.geo.Geo
        self.tables = data_tables  # type: polaris.network.data_table_cache.DataTableAccess

        self.__distances = {}
        self.__link_ids = {}
        self.__g = nx.Graph()
        self.__connec = pd.DataFrame([])
        self._network_file = geotools._network_file

    def short_links(self, threshold: float, returns="links") -> dict:
        """Queries links or nodes corresponding to links up to a certain length

        Args:
            *threshold* (:obj:`float`): Full path to the network file to be opened.
            *returns* (:obj:`str`): "links" for list of links shorter than threshold,
                                    and "nodes" for their corresponding nodes. Returns a node
                                    only if the link can be traversed by starting at that node
        Return:
            *report* (:obj:`dict`): Dictionary with length as key and list of nodes/links as values
        """
        dt = [threshold]
        if returns == "links":
            sql = 'select link, "length" from Link where "length"<? order by "length"'
        elif returns == "nodes":
            # We could omit the direction criteria for the purpose of this function
            # But the short_loops function could use this
            sql = '''select node, min("length") "length"
                     from (select node_a node, "length" from Link where "length"<? and lanes_ab>0
                           union all
                           select node_b node, "length" from Link where "length"<?  and lanes_ba>0)
                     group by node
                     order by "length"'''
            dt.append(threshold)
        else:
            raise ValueError('We can only return "links" or "nodes"')

        with read_and_close(self._network_file, spatial=True) as conn:
            data: Dict[float, List[int]] = {}
            for elem, dist in conn.execute(sql, dt).fetchall():
                q = data.get(dist, [])
                q.append(elem)
                data[dist] = sorted(q)

        return data

    def short_detours(self, threshold: float, returns="links") -> dict:
        """Computes all detours for a link where said detours are shorter than the threshold

        Args:
            *threshold* (:obj:`float`): Maximum length of detours to look for
            *returns* (:obj:`str`): Whether we want list of nodes or links traversed in the detour

        Return:
            *dict* (:obj:`dict`): Dictionary with all detours for the network. Keys are link IDS
                                  and values are dictionaries with keys equal to the detour length
                                  and values are lists of sequence of links or nodes traversed in the detour
        """
        # the only possible origins for our loops are the nodes that are attached to a link shorter
        # than the overall loop length and which we could traverse when starting from it
        sql = f"""select link, node_a node from Link where "length"<{threshold} and lanes_ab>0
                  union all
                  select link, node_b node from Link where "length"<{threshold} and lanes_ba>0"""

        self.__connec = self.tables.get("connection")[["link", "to_link"]]

        with read_and_close(self._network_file, spatial=True) as conn:
            data = pd.read_sql(sql, conn)

        # Loops are only possible if we have two links shorter than the
        data = data.groupby("node").link.nunique().reset_index()

        #
        data = data[data.link > 1]
        if data.empty:
            return {}

        all_links = self.tables.get("link")
        all_links = all_links[(all_links.node_a.isin(data.node)) | (all_links.node_b.isin(data.node))]

        # Builds the graph
        self.__nx__graph_builder(all_links)

        pairs_from = all_links[all_links.lanes_ab > 0][["link", "node_a", "node_b"]]
        pairs_from.columns = ["link", "f", "t"]

        pairs_to = all_links[all_links.lanes_ba > 0][["link", "node_b", "node_a"]]
        pairs_to.columns = ["link", "f", "t"]

        loops: Dict[int, Any] = {}
        for _, rec in pd.concat([pairs_from, pairs_to]).iterrows():  # type: (int, pd.Series)
            loop_data = self.__loop_finder(rec.f, rec.t, returns, threshold)
            if loop_data:
                dct = loops.get(rec.link, {})
                loops[rec.link] = {**dct, **loop_data}

        return loops

    def __loop_finder(self, f, t, returns, threshold) -> dict:
        paths = nx.shortest_simple_paths(self.__g, f, t, weight="weight")
        dct = {}  # type: Dict[int, list]
        for x in paths:
            if len(x) == 2:
                continue
            d = 0
            pth_lks = []
            for k in list(zip(x[:-1], x[1:])):
                if k not in self.__distances:
                    return dct
                pth_lks.append(self.__link_ids[k])
                d += self.__distances[k]
                if d > threshold:
                    return dct

            if returns == "links":
                m = 1
                for l1, l2 in zip(pth_lks[:-1], pth_lks[1:]):
                    m += self.__connec[(self.__connec.link == l1) & (self.__connec.to_link == l2)].shape[0]
                if m == len(pth_lks):
                    dct[d] = pth_lks
            elif returns == "nodes":
                dct[d] = x
            else:
                raise ValueError('The `returns` parameter must be equal to "links" or "nodes"')
        return dct

    def __nx__graph_builder(self, all_links):
        self.__g = nx.Graph()
        self.__distances.clear()
        self.__link_ids.clear()

        for _, rec in all_links.iterrows():
            if rec.lanes_ab > 0:
                self.__g.add_edge(rec.node_a, rec.node_b, weight=rec["length"])
                self.__distances[(rec.node_a, rec.node_b)] = rec["length"]
                self.__link_ids[(rec.node_a, rec.node_b)] = rec.link
            if rec.lanes_ba > 0:
                self.__g.add_edge(rec.node_b, rec.node_a, weight=rec["length"])
                self.__distances[(rec.node_b, rec.node_a)] = rec["length"]
                self.__link_ids[(rec.node_b, rec.node_a)] = rec.link
