# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import pandas as pd
from aequilibrae.paths import TrafficAssignment, TrafficClass

from polaris.prepare.supply_tables.network.utils import aematrix_single_values, build_centroids


def get_pedestrian_used_links(polaris_net, aeq_project, access_level, state_counties):
    """Obtains a list of links being used by the walk mode.
    Args:
        access_level (str): Whether to use locations, zones or block-groups as places of OD instead of zones
    Return:
        a list with of link ids
    """

    aeq_project.network.build_graphs(
        ["link_type", "capacity_ab", "capacity_ba", "distance", "free_flow_time"], modes=["w"]
    )
    graph = aeq_project.network.graphs["w"]
    graph.network.loc[:, "direction"] = 0

    # we give an advantage to road links over walk and bike ones to avoid having sidewalks running alongside roads that allow walking
    graph.network.loc[:, "free_flow_time"] = 60 * (graph.network.distance) / 1000 / 5.0
    graph.network.loc[graph.network.modes.str.contains("c"), "free_flow_time"] *= 0.1

    prohibited = ("motorway", "trunk", "centroid_connector", "steps", "track", "razed", "planned", "bridleway")
    sql = f"Select link_id from links where link_type in {prohibited}"
    with aeq_project.db_connection as conn:
        nolink_ids = pd.read_sql(sql, conn).link_id.to_numpy()
    graph.network = graph.network[~graph.network.link_id.isin(nolink_ids)]

    build_centroids(
        polaris_project=polaris_net,
        aeq_project=aeq_project,
        access_level=access_level,
        graph=graph,
        state_counties=state_counties,
        conn_speed=4.0,
    )

    matrix = aematrix_single_values(graph.centroids, "walk", 1.0)

    assigclass = TrafficClass("walk", graph, matrix)
    assig = TrafficAssignment()
    assig.set_classes([assigclass])
    assig.set_vdf("BPR")
    assig.set_vdf_parameters({"alpha": 0.1, "beta": 2})
    assig.set_capacity_field("distance")
    assig.set_time_field("free_flow_time")
    assig.set_algorithm("all-or-nothing")
    assig.max_iter = 2
    assig.rgap_target = 0.1
    assig.execute()
    df = assig.results()
    return df[df.PCE_tot > 0].reset_index().link_id.tolist()
