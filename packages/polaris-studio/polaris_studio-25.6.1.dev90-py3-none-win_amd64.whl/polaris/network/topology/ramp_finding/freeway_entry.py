# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from aequilibrae import PathResults

from polaris.network.network import Network
from polaris.network.topology.ramp_finding.utils import penalties, build_relevant_tables
from polaris.runs.static_assignment.static_graph import StaticGraph
from polaris.utils.python_signal import PythonSignal


def freeway_entries(supply_file: Path):
    net = Network.from_file(supply_file, False)
    graph = StaticGraph(net.path_to_file).graph
    graph.network = graph.network.assign(cost_ab=graph.network.distance, cost_ba=graph.network.distance)

    data = build_relevant_tables(net, graph)
    freeway_nodes = data["all_freeway_nodes"]
    only_freeway_nodes = data["only_freeway_nodes"]
    freeway_links = data["freeway_links"].link.to_numpy()
    surface_nodes = data["surface_nodes"]
    all_links = data["all_links"]

    graph.prepare_graph(graph.centroids)
    graph.network.time_ab = graph.network.distance
    graph.network.time_ba = graph.network.distance
    graph.set_graph("time")
    PENALTY, _ = penalties(graph)

    res = PathResults()
    res.prepare(graph)
    # The basic idea of the algorithm is to recursively build paths from a set of random nodes OUTSIDE the freeway
    # network to nodes that are part of the freeway network.

    # We penalize that link with a very high value, forcing the shortest path "around" that penalized link the next time
    # We compute it.

    # Since the freeway system is not necessarily all interconnected, we need to compute paths to ALL nodes in
    # the freeway network, to make sure we don't miss any entry points.

    np.random.seed(42)
    # We select up to 500 random non-freeway nodes to start the process, but don't ever get close to that
    sources = np.random.choice(surface_nodes, min(500, len(surface_nodes)), replace=False)

    link_types = np.empty(all_links.link.max() + 1, "<U20")  # all_links
    link_types[all_links.link] = all_links["type"].to_numpy().astype(str)

    all_tolls: list = []
    for source in sources:
        pbar = PythonSignal(object)
        pbar.emit(["start", "master", len(freeway_nodes), "Computing paths for origins"])
        pre_found = len(all_tolls)
        res.compute_path(source, int(freeway_nodes[-1]))
        for i_, target in enumerate(freeway_nodes):
            res.update_trace(int(target))
            pbar.emit(["update", "master", i_, f"Found {len(all_tolls):,} freeway entries"])
            while True:
                if res.path is None:
                    break
                common = np.isin(res.path, freeway_links)
                if np.any(
                    common
                ):  # There are freeway links in this path (i.e. it was not the endpoint of a freeway link where it meets another link type
                    if res.milepost[-1] >= PENALTY:
                        # If the freeway entry point has already been penalized, there is nothing else to be done here
                        break

                    # If we were able to get into the freeway without going through a penalized link, we identify the
                    # "entry" link as the first ramp the path included right before entering the freeway,
                    # or the first freeway link in the path, in case there are no ramps.
                    pre_ = np.argwhere(common)[0] - 1
                    pre = res.path[pre_][0]
                    post = res.path[common][0]
                    if link_types[pre].upper() == "RAMP":
                        toll = pre
                        dir_toll = res.path_link_directions[pre_][0]
                    else:
                        toll = post
                        dir_toll = res.path_link_directions[common][0]
                elif link_types[res.path[-1]].upper() == "RAMP" and target in only_freeway_nodes:
                    toll = res.path[-1]
                    dir_toll = res.path_link_directions[-1]
                else:
                    break

                # We penalize the link we found# And we penalize the link in the graph
                tolled_link = graph.graph.query("link_id==@toll and direction==@dir_toll").id.values[0]
                graph.cost[tolled_link] += PENALTY

                dir_toll = 0 if dir_toll == 1 else 1
                all_tolls.append([toll, dir_toll])
                res.compute_path(source, target)
                pbar.emit(["update_description", "master", i_, f"Found {len(all_tolls):,} freeway entries"])

        pbar.emit(["finished_procedure"])
        # We keep looping until we compute paths from a new node to all points in the freeway network and
        # don't find any new freeway entries
        if pre_found == len(all_tolls):
            # Re-ran from another origin and didn't change anything
            break
        logging.info(f"Found {len(all_tolls)} freeway entries. Looping around to make sure we didn't miss anything")
    return pd.DataFrame(all_tolls, columns=["link", "dir"]).assign(start_time=0, end_time=86400, price=1.0)
