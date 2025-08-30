# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from aequilibrae.paths import Graph, TrafficClass, TrafficAssignment
from scipy.spatial import Delaunay
from shapely.geometry.linestring import LineString

from polaris.analyze.mapping.utils import aggregation_layer
from polaris.network.utils.srid import get_table_srid
from polaris.skims.memory_matrix import MemoryMatrix
from polaris.utils.database.db_utils import read_and_close


def delaunay_assignment(supply_file: Path, aggregation: str, matrix: MemoryMatrix) -> gpd.GeoDataFrame:
    area_layer = aggregation_layer(supply_file, aggregation)

    dpoints = np.array(area_layer[["x", "y"]])
    all_edges = Delaunay(np.array(dpoints)).simplices
    edge_list = []
    for triangle in all_edges:
        links = list(combinations(triangle, 2))
        for i in links:
            f, t = sorted(i)
            edge_list.append(
                [
                    area_layer.at[f, "node_id"],
                    area_layer.at[t, "node_id"],
                    LineString([area_layer.at[f, "geo"], area_layer.at[t, "geo"]]),
                ]
            )

    edges = pd.DataFrame(edge_list, columns=["a_node", "b_node", "geometry"])
    edges.drop_duplicates(inplace=True)
    edges = gpd.GeoDataFrame(edges, geometry="geometry", crs=area_layer.crs)

    edges = edges.assign(direction=0, distance=edges.geometry.length, link_id=np.arange(edges.shape[0]) + 1)
    edges = edges[["link_id", "direction", "a_node", "b_node", "distance", "geometry"]]

    # AequilibraE logs too much, so let's turn it off for now
    os.environ["AEQ_SHOW_PROGRESS"] = "FALSE"
    logging.disable(logging.CRITICAL + 1)

    g = Graph()
    g.network = edges.assign(capacity=1)
    g.prepare_graph(centroids=area_layer.node_id)
    g.set_graph("distance")
    g.set_skimming("distance")
    g.set_blocked_centroid_flows(False)

    mat = matrix.to_aeq()
    if not mat.view_names:
        mat.computational_view()

    tc = TrafficClass("delaunay", g, mat)
    ta = TrafficAssignment()
    ta.set_classes([tc])
    ta.set_time_field("distance")
    ta.set_capacity_field("capacity")
    ta.set_vdf("BPR")
    ta.set_vdf_parameters({"alpha": 0, "beta": 1.0})
    ta.set_algorithm("all-or-nothing")
    ta.execute()

    cols = []
    for x in mat.view_names:
        cols.extend([f"{x}_ab", f"{x}_ba", f"{x}_tot"])
    df = ta.results()[cols].reset_index()
    logging.disable(logging.NOTSET)
    os.environ["AEQ_SHOW_PROGRESS"] = "TRUE"
    return edges.merge(df, on="link_id", how="inner")


def desire_lines(supply_file: Path, aggregation: str, matrix: MemoryMatrix) -> gpd.GeoDataFrame:
    area_layer = aggregation_layer(supply_file, aggregation)

    with read_and_close(supply_file, spatial=True) as conn:
        srid = get_table_srid(conn, "zone" if aggregation == "zone" else "Counties")
    matrices = matrix.to_df()

    area_layer = area_layer[["node_id", "geo"]]
    from_geo = matrices[["from_id", "to_id"]].merge(area_layer, left_on="from_id", right_on="node_id").geo.to_numpy()
    to_geo = matrices[["from_id", "to_id"]].merge(area_layer, left_on="to_id", right_on="node_id").geo.to_numpy()

    from_ = gpd.GeoSeries(from_geo, crs=srid)
    to_ = gpd.GeoSeries(to_geo, crs=srid)
    lines = from_.shortest_line(to_, True)

    matrices.rename(columns={"from_id": f"from_{aggregation}", "to_id": f"to_{aggregation}"}, inplace=True)
    return gpd.GeoDataFrame(matrices, geometry=lines, crs=srid)
