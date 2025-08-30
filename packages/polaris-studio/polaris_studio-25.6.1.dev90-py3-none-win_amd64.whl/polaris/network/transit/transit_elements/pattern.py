# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from os import PathLike
from pathlib import Path
from sqlite3 import Connection
from typing import List, Optional, Any, Tuple

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely.wkb
from polaris.network.constants import constants, PATTERN_ID_MULTIPLIER
from polaris.network.tools.geo import Geo
from polaris.network.transit.transit_elements.stop import Stop
from shapely.geometry import LineString
from shapely.ops import substring
from .basic_element import BasicPTElement
from .mode_correspondence import mode_correspondence

DEAD_END_RUN = 40


class Pattern(BasicPTElement):
    """Represents a stop pattern for a particular route, as defined in GTFS

    After loading a GTFS feed for a particular date, one can retrieve each
    pattern for analysis.  For example:

    ::

        from polaris.network.network import Network
        from os.path import join

        root = 'D:/Argonne/GTFS/DETROIT'

        n = Network()
        n.open(join(root, 'detroit-Supply.sqlite'))
        source = n.transit.new_gtfs(file_path=join(root, 'DDOT', '2020-06-23.zip'),
                              description='Detroit Department of Transportation',
                              agency_id='DDOT')

        source.load_date('2020-06-23')

        # We can access one pattern with its ID
        pat = source.select_patterns['D-d1079f93748abfdf57e28413874d3f54']

        # Or loop through all
        for pattern_id, pattern in source.select_patterns.items():
            # map_matching each one of them, for example
            pattern.map_match()

        # We can retrieve the issue in path finding we have for a pattern with

        #The pair of links between which there was an issue computing a path
        pair = pattern.get_error('culprit')

        # The reconstructed route until the point an issue was found
        pth = pattern.get_error('partial_path')

        # Once map_matching is complete (or re-done), one can update it in the database
        pattern.update_shape(n.conn)


    :Database class members:

        * pattern_id (:obj:`str`): Pattern ID as saved to the database
        * route_id (:obj:`str`): Route ID as saved to the database
        * seated_capacity (:obj:`int`): Vehicle seated capacity as saved to the database
        * design_capacity (:obj:`int`): Vehicle design capacity as saved to the database
        * total_capacity (:obj:`int`): Vehicle total capacity as saved to the database
        * shape (:obj:`LineString`): Route shape as saved to the database (populated by **map_match()**)

    :Other class members:

        * raw_shape (:obj:`LineString`): Route shape as retrieved from GTFS
        * route_type (:obj:`int`): GTFS route type
        * full_path (:obj:`List[int]`): Sequence list of links forming the path (negative for BA direction)
        * stops (:obj:`List[Stop]`): List of object stops in order of traversal by the route
        * network_candidates (:obj:`List[int]`): List of link IDs likely to be part of the route (populated by **find_network_links()**)
    """

    def __init__(self, geotool, route_id, gtfs_feed=None, path_to_file: PathLike = Path()) -> None:
        """
        Args:

            *pattern_id* (:obj:`str`): Pre-computed ID for this pattern
            *geotool* (:obj:`Geo`): Suite of geographic utilities. For internal use only
        """
        from polaris.network.tools.geo import Geo
        from polaris.network.transit.map_matching_graph import MMGraph
        from polaris.network.transit.functions.path_storage import PathStorage

        self.__path_to_file = path_to_file
        self.pattern_hash = ""
        self.pattern_id = -1
        self.route_id = route_id
        self.route = ""
        self.seated_capacity = None
        self.design_capacity = None
        self.total_capacity = None
        self.__geotool: Geo = geotool

        self.__feed = gtfs_feed
        self.__path_store = PathStorage() if gtfs_feed is None else gtfs_feed.path_store
        # For map matching
        self.raw_shape = LineString()
        self._stop_based_shape = LineString()
        self.shape = LineString()
        self.route_type: Optional[int] = None
        self.links: List[int] = []
        self.network_candidates: List[int] = []
        self.full_path: List[int] = []
        self.fpath_dir: List[int] = []
        self.pattern_mapping: List[List[Any]] = []
        self.stops: List[Stop] = []

        self.__graph: MMGraph
        self.__res = None
        self.__map_matched = False
        self.__match_quality = None
        self.shape_length = -1

    def save_to_database(self, conn: Connection, commit=True) -> None:
        """Saves the pattern to the *Transit_Patterns* table"""

        shp = self.best_shape()
        geo = None if shp is None else shp.wkb

        # path = '|'.join([str(int(x)) for x in self.full_path])
        data = [
            self.pattern_id,
            self.pattern_hash,
            self.route_id,
            self.__match_quality,
            self.seated_capacity,
            self.design_capacity,
            self.total_capacity,
            geo,
            self.__geotool.srid,
        ]

        sql = """insert into Transit_Patterns (pattern_id, pattern, route_id, matching_quality, seated_capacity,
                        design_capacity, total_capacity, geo) values (?, ?, ?, ?, ?, ?, ?, GeomFromWKB(?, ?));"""
        conn.execute(sql, data)

        if self.pattern_mapping and self.shape:
            sqlgeo = """insert into Transit_Pattern_Mapping(pattern_id, "index", link, dir, stop_id, offset, geo)
                        values (?, ?, ?, ?, ?, ?, GeomFromWKB(?, ?));"""
            sql = """insert into Transit_Pattern_Mapping (pattern_id, "index", link, dir, stop_id, offset)
                                                  values (?, ?, ?, ?, ?, ?);"""

            # The first map-matching segment needs to start at a stop
            if self.pattern_mapping[0][4] is not None:
                for record in self.pattern_mapping:
                    if record[-1] is None:
                        conn.execute(sql, record[:-1])
                    else:
                        geo = shapely.wkb.loads(record[-1])
                        if isinstance(geo, LineString):
                            conn.execute(sqlgeo, record + [self.__geotool.srid])
                        else:
                            conn.execute(sql, record[:-1])

        data = [[self.pattern_id, counter, link] for counter, link in enumerate(self.links)]
        conn.executemany('insert into Transit_Pattern_Links(pattern_id, "index", transit_link) values (?,?,?)', data)
        if commit:
            conn.commit()

    def best_shape(self) -> LineString:
        """Gets the best version of shape available for this pattern"""
        shp = self.raw_shape if self.raw_shape else self._stop_based_shape
        return self.shape if self.shape else shp

    def map_match(self):
        """Map matches the route into the network, considering its appropriate shape

        Part of the map-matching process is to find the network links corresponding the pattern's
        raw shape, so that method will be called in case it has not been called before.

        The basic algorithm behind the map-matching algorithm is described in https://doi.org/10.3141%2F2646-08

        In a nutshell, we compute the shortest path between the nodes corresponding to the links to which
        stops were geographically matched, for each pair of identified links.

        We do not consider links that are in perfect sequence, as we found that it introduces severe issues when
        stops are close to intersections without clear upsides.

         When issues are found, we remove the stops in the immediate vicinity of the issue and attempt new
         path finding. The First and last stops/corresponding links are always kept.

         If an error was found, (record for it will show in the log), it is stored within the object.

        """
        if self.__map_matched:
            return

        logging.debug(f"Map-matching pattern ID {self.pattern_id}")

        mode = mode_correspondence[self.route_type]
        if self.__feed is not None:
            if not self.__path_store.graphs:
                self.__feed.builds_link_graphs_with_broken_stops()

            if mode not in self.__feed.graphs:
                return
            self.__path_store.add_graph(self.__feed.graphs[mode], mode)
        else:
            from polaris.network.transit.map_matching_graph import MMGraph

            mm = MMGraph(
                Geo(self.__path_to_file), {stop.stop_id: stop for stop in self.stops}, "BESPOKE", "map-matching"
            )
            graph = mm.build_graph_with_broken_stops(self.route_type)
            if graph.num_links <= 0:
                return
            self.__path_store.add_graph(graph, mode)

        df = self.__map_matching_complete_path_building()
        if df.empty:
            logging.warning(f"Could not rebuild path for pattern {self.pattern_id}")
            return
        self.full_path = df.link_id.to_list()
        self.fpath_dir = df.dir.to_list()
        self.__assemble__mm_shape(df)
        self.__build_pattern_mapping()
        logging.info(f"Map-matched pattern {self.pattern_id}")

    def __graph_discount(self, connected_stops):
        link_lyr = self.__geotool.get_link_layer_by_mode(mode_correspondence[self.route_type])
        pts = gpd.GeoSeries([stop.geo for stop in connected_stops]).buffer(40)
        filtered_lyr = link_lyr.sjoin(gpd.GeoDataFrame(geometry=pts), how="left", predicate="intersects")
        return list(set(filtered_lyr.link.tolist()))

    def __map_matching_complete_path_building(self):
        mode_ = mode_correspondence[self.route_type]
        # We get the graph for our job
        graph = self.__path_store.graphs[mode_]
        empty_frame = pd.DataFrame([])

        # We search for disconnected  :
        candidate_stops = list(self.stops)
        stop_node_idxs = [stop.___map_matching_id__[self.route_type] for stop in candidate_stops]

        node0 = graph.network.a_node[~graph.network.a_node.isin(graph.centroids)].min()
        connected_stops = []
        for i, stop in enumerate(candidate_stops):
            node_o = stop.___map_matching_id__[self.route_type]
            logging.debug(f"Computing paths between {node_o} and {node0}")
            res = self.__path_store.get_path_results(node_o, mode_)
            res.update_trace(int(node0))

            # Get skims, as proxy for connectivity, for all stops other than the origin
            other_nodes = stop_node_idxs[:i] + stop_node_idxs[i + 1 :]
            dest_skim = res.skims[other_nodes, 0]
            if dest_skim.min() < 1.0e308:
                candidate_stops = candidate_stops[i:]
                connected_stops = [stop for i, stop in enumerate(candidate_stops[1:]) if dest_skim[i] < 1.0e308]
                connected_stops = [candidate_stops[0]] + connected_stops
                break

        if not connected_stops:
            logging.critical(f"Route completely disconnected. {self.route}/{self.route_id}")
            return empty_frame

        graph.cost = np.array(graph.graph.distance)
        likely_links = self.__graph_discount(connected_stops)
        graph.cost[graph.graph.original_id.abs().isin(likely_links)] *= 0.1

        fstop = connected_stops[0]

        if len(connected_stops) == 1:
            return empty_frame

        if len(connected_stops) == 2:
            nstop = connected_stops[1].___map_matching_id__[self.route_type]
            logging.debug(f"Computing paths between {fstop.___map_matching_id__[self.route_type]} and {nstop}")
            res = self.__path_store.get_path_results(fstop.___map_matching_id__[self.route_type], mode_)
            res.update_trace(int(nstop))
            if not res.milepost.sum():
                return empty_frame
            pdist = list(res.milepost[1:-1] - res.milepost[:-2])[1:]
            plnks = list(res.path[1:-1])
            pdirecs = list(res.path_link_directions[1:-1])
            return self.__build_path_df(graph, pdirecs, pdist, plnks)

        path_links = []
        path_directions = []
        path_distances = []
        start = fstop.___map_matching_id__[self.route_type]
        for idx, tstop in enumerate(connected_stops[1:]):
            end = tstop.___map_matching_id__[self.route_type]

            not_last = idx + 2 <= len(connected_stops) - 1

            if not_last:
                following_stop = connected_stops[idx + 2]
                n_end = following_stop.___map_matching_id__[self.route_type]
            logging.debug(f"Computing paths between {start} and {end}")
            res = self.__path_store.get_path_results(start, mode_)
            res.update_trace(int(end))
            connection_candidates = graph.network[graph.network.a_node == end].b_node.values
            min_cost = np.inf
            access_node = -1
            follow_val = 0
            for connec in connection_candidates:
                if connec == start:
                    continue
                if not_last:
                    res1 = self.__path_store.get_path_results(connec, mode_)
                    res1.update_trace(int(n_end))
                    if res1.milepost is None:
                        continue
                    follow_val = res1.milepost[-1]
                estimate = follow_val + res.skims[connec, 0]
                if estimate < min_cost:
                    min_cost = estimate
                    access_node = connec
            if access_node >= 0:
                res.update_trace(int(access_node))
                shift = 1 if not_last else 0
                if len(res.path) <= 1 + shift:
                    # Stop connectors only
                    continue

                if not_last:
                    path_links.extend(list(res.path[:-1]))
                    path_directions.extend(list(res.path_link_directions[:-1]))
                    path_distances.extend(list(res.milepost[1:] - res.milepost[:-1])[1:])
                else:
                    path_links.extend(list(res.path[:]))
                    path_directions.extend(list(res.path_link_directions[:]))
                    path_distances.extend(list(res.milepost[1:] - res.milepost[:-1])[:])
            else:
                logging.debug(f"Failed path computation when map-matching {self.pattern_id}")
                return empty_frame
            start = res.path_nodes[-2] if len(res.path_nodes) > 3 else start

        # Connection to the last stop
        return self.__build_path_df(graph, path_directions, path_distances, path_links)

    def __build_path_df(self, graph, path_directions, path_distances, path_links):
        corresp = pd.DataFrame(graph.network[["link_id", "original_id"]])
        if not path_links:
            return pd.DataFrame({"link_id": [], "dir": []})
        result = pd.DataFrame(
            {
                "link_id": path_links[:],
                "direction": path_directions[:],
                "sequence": np.arange(len(path_links)),
                "distance": path_distances[:],
            }
        )
        df = result.merge(corresp, on="link_id", how="left")
        df.sort_values(by=["sequence"], inplace=True)  # We just guarantee that we haven't messed up anything
        df = df[(df.link_id.shift(-1) != df.link_id) | (df.direction.shift(-1) != df.direction)]

        crit1 = df.original_id.shift(1) * df.direction.shift(-1) != df.original_id * df.direction
        df = df[(crit1) | (df.distance > DEAD_END_RUN)]
        df = df[df.original_id > 0]

        df = df[["original_id", "direction"]]
        df.columns = ["link_id", "dir"]
        df.reset_index(drop=True, inplace=True)
        has_issues = True
        while has_issues:
            # We eliminate multiple backs-and-forth on links
            has_issues = False
            for i in range(0, df.shape[0] - 2):
                if df.loc[i : i + 2, "link_id"].abs().unique().shape[0] == 1:
                    df.drop(index=[i, i + 1], inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    has_issues = True
                    break
        return df

    def __assemble__mm_shape(self, df: pd.DataFrame):
        shape: List[Tuple[float, float]] = []
        link_lyr = self.__geotool.get_geo_layer("link")
        for _, rec in df.iterrows():
            line_geo = link_lyr[link_lyr.link == rec.link_id].geo.values[0]
            coords = list(line_geo.coords)[::-1] if rec.dir < 0 else list(line_geo.coords)
            data = coords[1:] if shape else coords
            shape.extend(data)
        self.shape = LineString(shape)

    def __build_pattern_mapping(self):
        # We find what is the position along routes that we have for each stop and make sure they are always growing
        self.pattern_mapping = []
        link_lyr = self.__geotool.get_geo_layer("link")
        segments = [LineString([pt1, pt2]) for pt1, pt2 in zip(self.shape.coords, self.shape.coords[1:]) if pt1 != pt2]
        seg_len = [seg.length for seg in segments]
        distances = []

        min_idx_so_far = 0
        for i, stop in enumerate(self.stops):
            d = [round(stop.geo.distance(line), 1) for line in segments]
            idx = d[min_idx_so_far:].index(min(d[min_idx_so_far:])) + min_idx_so_far
            idx = idx if i > 0 else 0
            projection = segments[idx].project(stop.geo) + sum(seg_len[:idx])
            distances.append(projection)
            min_idx_so_far = idx

        # the list needs to be monotonically increasing
        if not all(x <= y for x, y in zip(distances, distances[1:])):
            for i, (x, y) in enumerate(zip(distances, distances[1:])):
                distances[i + 1] = distances[i] if y < x else distances[i + 1]

            logging.warning(
                f"""Pattern {self.pattern_id} has a map-matching pattern resulting in backwards movement.
                            It was fixed, but it should be checked."""
            )

        distances[-1] = distances[-1] if self.shape.length > distances[-1] else self.shape.length - 0.00001

        # We make sure we don't have projections going beyond the length we will accumulate
        # This is only required because of numerical precision issues
        tot_broken_length = np.sum(link_lyr[link_lyr.link.isin(self.full_path)].geometry.length)
        distances = [min(x, tot_broken_length) for x in distances]
        pid = self.pattern_id
        stop_pos = cum_dist = index = 0
        for link_pos, link_id in enumerate([abs(x) for x in self.full_path]):
            direc = 1 if self.fpath_dir[link_pos] == -1 else 0
            link_geo = link_lyr[link_lyr.link == link_id].geo.values[0]
            link_geo = link_geo if direc == 0 else LineString(link_geo.coords[::-1])
            if distances[stop_pos] > cum_dist + link_geo.length:
                # If we have no stops falling right in this link
                dt = [pid, index, link_id, direc, None, None, link_geo.wkb]
                self.pattern_mapping.append(dt)
                index += 1
                cum_dist += link_geo.length
                continue

            start_point = cum_dist
            end_point = cum_dist + link_geo.length
            while cum_dist + link_geo.length >= distances[stop_pos]:
                milepost = distances[stop_pos]
                wkb = None if stop_pos == 0 else substring(self.shape, start_point, milepost).wkb
                stop = self.stops[stop_pos]
                dt = [pid, index, link_id, direc, stop.stop_id, milepost - cum_dist, wkb]
                self.pattern_mapping.append(dt)
                index += 1

                stop_pos += 1
                if stop_pos >= len(distances):
                    break
                start_point = milepost

            cum_dist += link_geo.length

            if start_point != end_point:
                wkb = substring(self.shape, start_point, end_point).wkb
                self.pattern_mapping.append([pid, index, link_id, direc, None, None, wkb])
                index += 1

            if stop_pos >= len(distances):
                break
        self.__compute_match_quality()

    def __compute_match_quality(self):
        dispersion = [self.shape.distance(stop.geo) for stop in self.stops]

        dispersion = sum([x * x for x in dispersion]) / len(self.stops)
        self.__match_quality = dispersion

    def get_pattern_id(self):
        if self.pattern_id != -1:
            return

        c = constants()
        self.pattern_id = c.patterns.get(self.route_id, self.route_id) + PATTERN_ID_MULTIPLIER
        c.patterns[self.route_id] = self.pattern_id
