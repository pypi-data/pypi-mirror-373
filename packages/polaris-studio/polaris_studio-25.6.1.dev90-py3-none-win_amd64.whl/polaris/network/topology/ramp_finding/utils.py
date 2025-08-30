# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import numpy as np

freeway_types = ["EXPRESSWAY", "FREEWAY"]
freeway_types_and_ramps = freeway_types + ["RAMP"]


def penalties(graph):
    exponent = np.ceil(np.log10(graph.graph.distance.sum()))
    return 10 ** (exponent + 3), 10 ** (exponent)


def build_relevant_tables(net, graph):
    assert len(freeway_types) > 0

    links = net.tables.get("link")
    links.loc[links["type"] == "EXPRESSWAY", "type"] = "FREEWAY"

    nodes = net.tables.get("node")
    assert nodes.size > 0

    freeway_links = links.query("type in @freeway_types")
    surface_streets = links.query("type not in @freeway_types")
    surface_streets_no_ramps = links.query("type not in @freeway_types_and_ramps")
    ramps = links.query("type == 'RAMP'")

    all_freeway_nodes = np.unique(np.hstack([freeway_links.node_a.to_numpy(), freeway_links.node_b.to_numpy()]))
    all_surface_nodes = np.unique(np.hstack([surface_streets.node_a.to_numpy(), surface_streets.node_b.to_numpy()]))
    ramp_nodes = np.unique(np.hstack([ramps.node_a.to_numpy(), ramps.node_b.to_numpy()]))

    # Freeway nodes
    only_freeway_nodes = all_freeway_nodes[~np.isin(all_freeway_nodes, ramp_nodes)]
    only_freeway_nodes = only_freeway_nodes[~np.isin(only_freeway_nodes, all_surface_nodes)]

    # And surface street nodes that also have no ramp connected to them
    surface_nodes = np.unique(
        np.hstack([surface_streets_no_ramps.node_a.to_numpy(), surface_streets_no_ramps.node_b.to_numpy()])
    )

    surface_nodes = surface_nodes[~np.isin(surface_nodes, ramp_nodes)]

    link_id = graph.network.link_id.min()
    assert link_id is not None
    node_net = links.query("link==@link_id").node_a.values[0]
    node_graph = graph.network.query("link_id==@link_id").a_node.values[0]
    node_shift = node_graph - node_net

    data = {
        "only_freeway_nodes": only_freeway_nodes + node_shift,
        "all_freeway_nodes": all_freeway_nodes + node_shift,
        "surface_nodes": surface_nodes + node_shift,
        "freeway_links": freeway_links,
        "node_shift": node_shift,
        "all_links": links,
    }

    return data
