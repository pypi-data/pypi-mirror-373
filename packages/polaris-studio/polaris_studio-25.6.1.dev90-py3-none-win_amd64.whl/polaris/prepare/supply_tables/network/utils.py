# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import geopandas as gpd
import numpy as np
import pandas as pd
import pygris
from aequilibrae.matrix import AequilibraeMatrix

from polaris.utils.database.data_table_access import DataTableAccess
from scipy.spatial import cKDTree

# This needs input form the team.

dict_modes = {
    "car": {"codes": [0, 1, 2, 3], "pce": 1.0},  # 0=SOV 1=AUTO_NEST 2=HOV 3=TRUCK
    "light_truck": {"codes": [18, 19], "pce": 2.5},  # 18=HD_TRUCK 19=BPLATE
    "heavy_truck": {"codes": [17, 20], "pce": 3.5},  # 17=MD_TRUCK 20=LD_TRUCK
}


def aematrix_single_values(centroids, mat_name, demand_val):
    centroids.sort()
    n_centroids = len(centroids)
    mat = AequilibraeMatrix()
    mat.create_empty(zones=n_centroids, matrix_names=[mat_name], memory_only=True)
    mat.index = centroids
    mat.indices = mat.indices.astype(int)
    matrix_vals = np.empty((n_centroids, n_centroids))
    matrix_vals.fill(demand_val)

    mat.matrix[mat_name][:, :] = matrix_vals[:, :]
    mat.computational_view()
    return mat


def build_centroids(polaris_project, aeq_project, state_counties, access_level, graph, conn_speed):
    df_nodes = aeq_project.network.nodes.data
    gdf_nodes = gpd.GeoDataFrame(df_nodes, geometry=df_nodes["geometry"], crs="EPSG:4326").to_crs(3857)

    # Zone centroids we will use for our process
    proj_path = polaris_project.path_to_file
    if access_level.lower() in ["zone", "location"]:
        loc_type = access_level
        gdf_cntrds = DataTableAccess(proj_path).get(loc_type).to_crs(3857)
    elif access_level.lower() == "block-groups":
        dt = []
        for _, rec in state_counties.iterrows():
            kwargs = {"state": rec["state_name"], "county": rec["COUNTYFP"], "year": 2021, "cache": True}
            dt.append(pygris.block_groups(**kwargs))

        if len(dt) == 0:
            raise ValueError(
                "Could not find any US State/county that overlaps the desired modeling area. select a different access level for the simplification"
            )

        candidates = gpd.GeoDataFrame(pd.concat(dt), geometry=dt[0]._geometry_column_name, crs=dt[0].crs.to_epsg())
        model_area = DataTableAccess(proj_path).get("Zone").to_crs(candidates.crs.to_epsg(10))
        gdf_cntrds = candidates[candidates.intersects(model_area.union_all())]
        gdf_cntrds = gdf_cntrds.to_crs(3857)
    else:
        raise ValueError("Invalid access level. Access levels available: 'zone', 'location', 'block-groups'")

    # We have our centroids ready
    gdf_cntrds.geometry = gdf_cntrds.geometry.centroid
    geo_col = gdf_cntrds._geometry_column_name
    gdf_cntrds = gdf_cntrds.assign(__cid__=np.arange(gdf_cntrds.shape[0]) + 1)[["__cid__", geo_col]]
    gdf_cntrds.reset_index(drop=True, inplace=True)
    centr_coords = gdf_cntrds.geometry.apply(lambda geom: (geom.x, geom.y)).tolist()

    # Let's renumber the graph's nodes to make space for these new centroids
    graph.network[["a_node", "b_node"]] += gdf_cntrds.shape[0] + 2

    # Now we will connect both the closest node in the graph, as well as the
    # two closest CAR nodes in the graph
    # All nodes that will be allowed to act as centroids
    net_car = graph.network[graph.network.modes.str.contains("c")]
    allowed_nodes_car = np.unique(np.hstack((net_car.a_node, net_car.b_node)))

    all_connectors = []
    for allowed_nodes, mult in [[allowed_nodes_car, 0.1]]:
        nds_ = gdf_nodes[gdf_nodes.node_id.isin(allowed_nodes)]
        nds_.reset_index(drop=True, inplace=True)

        tree = cKDTree(nds_.geometry.apply(lambda geom: (geom.x, geom.y)).tolist())

        # We get the three closest nodes
        distances, indices = tree.query(centr_coords, k=3)
        for i in range(3):
            df = pd.DataFrame(
                {
                    "node_id": nds_.node_id.values[indices[:, i]],
                    "__cid__": gdf_cntrds["__cid__"].values,
                    "distance": distances[:, i],
                }
            )
            df = df.assign(free_flow_time=mult * 60 * (df.distance / 1000) / conn_speed)  # in minutes
            all_connectors.append(df)

    conns = pd.concat(all_connectors).rename(columns={"__cid__": "a_node", "node_id": "b_node"})
    conns.drop_duplicates(subset=["a_node", "b_node"], inplace=True)
    conns = conns.assign(
        direction=0,
        link_id=np.arange(conns.shape[0]) + graph.network.link_id.max() + 1,
        capacity_ab=100000,
        capacity_ba=100000,
    )

    graph.network = pd.concat([graph.network, conns], ignore_index=True).fillna(0)

    graph.prepare_graph(gdf_cntrds["__cid__"].to_numpy().astype(np.int64))
    graph.set_graph("free_flow_time")
    graph.set_skimming(["free_flow_time"])
    graph.set_blocked_centroid_flows(True)
