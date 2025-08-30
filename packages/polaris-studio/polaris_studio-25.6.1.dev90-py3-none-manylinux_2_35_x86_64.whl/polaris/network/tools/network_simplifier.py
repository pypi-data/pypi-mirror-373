# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import warnings
from copy import deepcopy
from math import ceil
from os import PathLike
from typing import List

import numpy as np
import pandas as pd
from shapely.geometry.linestring import LineString
from shapely.ops import linemerge
from shapely.ops import substring

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.utils.srid import get_srid
from polaris.runs.static_assignment.static_graph import StaticGraph
from polaris.utils.database.db_utils import commit_and_close
from polaris.utils.signals import SIGNAL


class NetworkSimplifier:
    def __init__(self, network_database_path: PathLike):
        self.network_file = network_database_path
        self.dtc = DataTableAccess(self.network_file)
        self.link_layer = self.dtc.get("Link")
        warnings.warn("This will alter your database in place. Make sure you have a backup.")

    def simplify(self, maximum_allowable_link_length=1000, max_speed_ratio=1.1):
        """
        Simplifies the network by merging links that are shorter than a given threshold
        Args:
            *maximum_allowable_link_length* (:obj:`float`): Maximum length for output links (meters)
            *max_speed_ratio* (:obj:`float`): Maximum ratio between the fastest and slowest speed for a link to be considered for simplification
        """

        # Builds the AequilibraE graph from which we will get the topological simplification results
        aeq_graph = StaticGraph(self.network_file).graph
        aeq_graph.prepare_graph(aeq_graph.centroids, False)
        # Creates the sequence of compressed link IDs so we don't have to rebuild through path computation
        compressed_idx, compressed_link_data, _ = aeq_graph.create_compressed_link_network_mapping()

        link_set_df = aeq_graph.network.merge(aeq_graph.graph[["link_id", "__compressed_id__"]], on="link_id")

        # compressed_ids that appear for more than one link
        relevant_compressed_ids = pd.DataFrame(link_set_df.value_counts("__compressed_id__")).query("count>1").index
        link_set_df = link_set_df[link_set_df.__compressed_id__.isin(relevant_compressed_ids)]

        # Makes sure we always get the compressed Id for the same (arbitrary) direction
        link_set_df = link_set_df.sort_values("__compressed_id__").drop_duplicates(subset="link_id", keep="first")

        # We only need one link ID per "super link"
        link_set_df = link_set_df.drop_duplicates(subset="__compressed_id__")
        centroid_connectors = aeq_graph.network.query("link_id not in @self.link_layer.link").link_id.to_numpy()

        links_to_delete, new_links = [], []
        max_link_id = self.link_layer.link.max() + 1
        pbar = SIGNAL(object)
        pbar.emit(["start", "master", link_set_df.shape[0], "Simplifying links"])

        for _, rec in link_set_df.iterrows():
            pbar.emit(["update", "master", None, None])
            compressed_id = rec.__compressed_id__

            # We got to the group of links where AequilibraE can no longer compress
            if compressed_id + 1 == compressed_idx.shape[0]:
                continue
            link_sequence = compressed_link_data[compressed_idx[compressed_id] : compressed_idx[compressed_id + 1]]
            if len(link_sequence) < 2:
                continue

            link_sequence = np.abs(link_sequence)
            candidates = self.link_layer.query("link in @link_sequence").set_index("link")
            link_sequence = [x for x in link_sequence if x not in centroid_connectors]

            if candidates.shape[0] <= 1 and candidates["length"].sum() < maximum_allowable_link_length:
                continue

            # To merge, all links have to have the same number of lanes, and functional class
            breaker = candidates["type"].nunique() > 1
            if breaker:
                continue

            # We build the geometry sequence
            # We also build speeds, capacities
            candidates, geos, long_dir, long_lnk = self.__process_link_fields(
                candidates, link_sequence, max_speed_ratio
            )

            if candidates.empty:
                continue

            new_geo = linemerge(geos)
            if not isinstance(new_geo, LineString):
                warnings.warn(f"Failed to merge geometry for superlink around link {rec.link_id}")
                continue

            break_into = ceil(new_geo.length / maximum_allowable_link_length)

            # Now we build the template for the links we will build
            main_data = long_lnk.to_dict()

            # Some values we will bring from the weighted average
            for field in ["fspd_ab", "fspd_ba", "grade", "cap_ab", "cap_ba"]:
                metric = (candidates[field] * candidates["length"]).sum() / candidates["length"].sum()
                if long_dir == 1 or field in ["grade"]:
                    main_data[field] = metric
                else:
                    field2 = field.replace("ab", "ba") if "ab" in field else field.replace("ba", "ab")
                    main_data[field2] = metric

            # If that link is in the opposite direction, we need to swap lanes, as we would have swapped the geometry as well
            if long_dir == -1:
                main_data["lanes_ab"], main_data["lanes_ba"] = main_data["lanes_ba"], main_data["lanes_ab"]

            # Area type is the most common
            groupby_ = candidates[["area_type", "length"]].groupby("area_type")
            main_data["area_type"] = groupby_.sum().sort_values("length", ascending=False).iloc[0].name

            if not candidates.query("toll_counterpart > 0").empty:
                main_data["toll_counterpart"] = -1

            for i in range(break_into):
                data = deepcopy(main_data)
                data["link"] = max_link_id

                sub_geo = substring(new_geo, i / break_into, (i + 1.0) / break_into, normalized=True)
                if sub_geo.length < 0.000001:
                    raise ValueError("Link with zero length")

                data["geo"] = sub_geo.wkb
                max_link_id += 1
                new_links.append(data)
            links_to_delete.extend(candidates.index.tolist())

        logging.info(f"{len(links_to_delete):,} links will be removed")
        logging.info(f"{len(new_links):,} links will be added")
        if new_links:
            self.__execute_link_deletion_and_addition(new_links, links_to_delete)

        logging.warning("Network has been rebuilt. You should run this tool's rebuild network method")

    def __process_link_fields(self, candidates, link_sequence, max_speed_ratio):
        candidates = candidates.loc[link_sequence]
        lnk = candidates.loc[link_sequence[0]]
        start_node = (
            lnk.node_a if candidates.query("node_a==@lnk.node_a or node_b==@lnk.node_b").shape[0] == 1 else lnk.node_b
        )
        longest_link_id = candidates.sort_values("length", ascending=False).index[0]
        fspds_ab, fspds_ba, geos, lanes_ab, lanes_ba = [], [], [], [], []
        longest_link, longest_direction = None, None
        for link_id in link_sequence:
            link = candidates.loc[link_id]
            direction = "AB" if start_node == link.node_a else "BA"
            geos.append(link.geo if direction == "AB" else link.geo.reverse())
            fspds_ab.append(link.fspd_ab if direction == "AB" else link.fspd_ba)
            fspds_ba.append(link.fspd_ba if direction == "AB" else link.fspd_ab)
            lanes_ab.append(link.lanes_ab if direction == "AB" else link.lanes_ba)
            lanes_ba.append(link.lanes_ba if direction == "AB" else link.lanes_ab)
            if link_id == longest_link_id:
                # We use the longest link as a template
                longest_direction = 1 if direction == "AB" else -1
                longest_link = link
            start_node = link.node_b if direction == "AB" else link.node_a
        constraints_broken = int(np.unique(lanes_ab).shape[0] > 1)
        constraints_broken += np.unique(lanes_ba).shape[0] > 1
        # Speeds cannot diverge by more than 10%
        constraints_broken += max(fspds_ab) / max(min(fspds_ab), 0.00001) > max_speed_ratio
        constraints_broken += max(fspds_ba) / max(min(fspds_ba), 0.00001) > max_speed_ratio
        if constraints_broken > 0:
            return pd.DataFrame([]), None, None, None
        return candidates, geos, longest_direction, longest_link

    def __execute_link_deletion_and_addition(self, new_links, links_to_delete):
        df = pd.DataFrame(new_links)
        df.drop(columns=["node_a", "node_b"], inplace=True)
        cols = list(df.columns)
        cols.remove("geo")
        cols.append("geo")
        df = df[cols]
        data = df.assign(srid=self.link_layer.crs.to_epsg()).to_records(index=False)

        sql = f"INSERT INTO Link({','.join(df.columns)}) VALUES ({','.join(['?'] * (len(df.columns) - 1))},GeomFromWKB(?, ?))"
        with commit_and_close(self.network_file, spatial=True) as conn:
            conn.executemany(sql, data)
            conn.executemany("DELETE FROM Link WHERE link=?", [[x] for x in links_to_delete])
            conn.commit()

        # Validate that we kept distances the same
        old_dist = self.link_layer.geometry.length.sum()
        self.dtc.refresh_cache()
        new_layer = self.dtc.get("Link")
        new_dist = new_layer.geometry.length.sum()

        logging.warning(f"Old distance: {old_dist}, new distance: {new_dist}. Difference: {old_dist - new_dist}")
        self.link_layer = new_layer

    def collapse_links_into_nodes(self, links: List[int]):
        srid = get_srid(database_path=self.network_file)
        target_links = self.link_layer.query("link in @links")
        with commit_and_close(self.network_file, spatial=True) as conn:
            for _, link in target_links.iterrows():
                wkb = link.geo.interpolate(0.5, normalized=True).wkb
                conn.execute("DELETE FROM Link WHERE link=?", [link.link])
                conn.commit()
                conn.execute("UPDATE Node set geo=GeomFromWKB(?, ?) where node=?", [wkb, srid, link.node_a])
                conn.execute("UPDATE Node set geo=GeomFromWKB(?, ?) where node=?", [wkb, srid, link.node_b])
                conn.commit()

        logging.warning(f"{len(links)} links collapsed into nodes")

    def rebuild_network(self):
        # Rebuilds the network elements that would have to be rebuilt after massive network simplification
        from polaris.network.network import Network

        net = Network.from_file(self.network_file, False)
        net.full_rebuild()

        with commit_and_close(self.network_file, spatial=True) as conn:
            conn.execute("VACUUM")
        net.checker.errors.clear()
        net.checker.critical()
        if len(net.checker.errors):
            logging.error(f"Errors found after rebuilding the network. {net.checker.errors}")
