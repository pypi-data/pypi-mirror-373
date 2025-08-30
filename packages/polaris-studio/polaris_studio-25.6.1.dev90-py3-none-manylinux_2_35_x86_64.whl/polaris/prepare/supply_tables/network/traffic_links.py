# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import math

from aequilibrae.paths import TrafficAssignment, TrafficClass

from polaris.prepare.supply_tables.network.utils import aematrix_single_values, build_centroids


def get_car_used_links(polaris_net, aeq_project, access_level, state_counties, maximum_capacity):
    """Obtains a list of links being used by the car mode.
    Args:
        access_level (str): Whether to use locations, zones or block-groups as places of OD instead of zones

        maximum_capacity(bool): Whether we should attempt to run an equilibrium assignment to spread more flows
    Return:
        a list with of link ids
    """

    algorithm = "bfw" if maximum_capacity else "all-or-nothing"

    aeq_project.network.build_graphs(["capacity_ab", "capacity_ba", "distance", "free_flow_time"], modes=["c"])
    graph = aeq_project.network.graphs["c"]

    build_centroids(
        polaris_project=polaris_net,
        aeq_project=aeq_project,
        access_level=access_level,
        graph=graph,
        state_counties=state_counties,
        conn_speed=20,
    )

    # Heuristic value
    demand_val = 1.0 / (10 ** math.floor(math.log10(graph.centroids.shape[0])))

    df = used_links_traffic(graph, demand_val, algorithm=algorithm)

    df_links = aeq_project.network.links.data
    main_roads = ["primary", "secondary", "tertiary", "trunk", "highway", "motorway", "freeway"]
    keep_roads = df_links[df_links.link_type.isin(main_roads)].link_id.values
    df_links = df_links[(df_links.link_id.isin(df.link_id.to_numpy())) | (df_links.link_id.isin(keep_roads))]
    return df_links.link_id.values.tolist()


def used_links_traffic(graph, demand_val, algorithm="bfw", max_iterations=50):
    matrix = aematrix_single_values(graph.centroids, "demand", demand_val)
    assig = TrafficAssignment()
    assigclass = TrafficClass(name="car_usage", graph=graph, matrix=matrix)
    assig.add_class(assigclass)
    assig.set_vdf("BPR")
    assig.set_vdf_parameters({"alpha": 0.1, "beta": 2.0})

    cap_field = "capacity" if "capacity" in graph.graph.columns else "cap"
    assig.set_capacity_field(cap_field)

    time_field = "free_flow_time" if "free_flow_time" in graph.graph.columns else "time"
    assig.set_time_field(time_field)
    assig.set_algorithm(algorithm)
    assig.max_iter = max_iterations
    assig.rgap_target = 0.001
    assig.execute()
    df = assig.results().reset_index()
    return df[df.PCE_tot > 0]
