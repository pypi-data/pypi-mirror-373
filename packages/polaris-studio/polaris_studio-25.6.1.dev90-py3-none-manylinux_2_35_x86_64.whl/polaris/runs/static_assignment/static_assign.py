# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import multiprocessing as mp
from typing import Dict

import numpy as np
from aequilibrae.paths.network_skimming import NetworkSkimming
from aequilibrae.paths.traffic_assignment import TrafficAssignment
from aequilibrae.paths.traffic_class import TrafficClass

from polaris.runs.static_assignment.static_assignment_inputs import STAInputs


def static_assignment(graph, matrix, assig_pars: STAInputs) -> TrafficAssignment:
    if matrix.matrix_view.sum() == 0:
        return TrafficAssignment()

    assig = TrafficAssignment()
    assigclass = TrafficClass(name="combined", graph=graph, matrix=matrix)  # Create the assignment class
    assigclass.set_fixed_cost("connector_penalty", 1.0)

    assig.add_class(assigclass)  # The first thing to do is to add at list of traffic classes to be assigned

    assig.set_vdf("BPR")  # Set tge VDF
    assig.set_vdf_parameters({"alpha": assig_pars.bpr_alpha, "beta": assig_pars.bpr_beta})  # And its parameters

    assig.set_capacity_field("capacity")  # The capacity and free flow travel times as they exist in the graph
    assig.set_time_field("time")

    assig.set_algorithm(assig_pars.assignment_algorithm)  # And the algorithm we want to use to assign

    assig.max_iter = assig_pars.max_iterations
    assig.rgap_target = assig_pars.rgap
    assig.set_cores(mp.cpu_count())

    assig.execute()  # we then execute the assignment
    return assig


def assign_with_skim(graph, matrix, assig_pars: STAInputs):
    if matrix.matrix_view.sum() == 0:
        logging.warning("NO DEMAND RECORDED")
        ns = NetworkSkimming(graph)
        ns.execute()

        distance = ns.results.skims.distance.astype(np.float32)
        ttime = ns.results.skims.time.astype(np.float32)
        return {"distance": distance, "time": ttime, "cost": np.zeros_like(ttime)}

    assig = static_assignment(graph, matrix, assig_pars)

    assert not np.any(np.isinf(assig.classes[0].results.skims.distance))
    assert not np.any(np.isinf(assig.classes[0].results.skims.time))

    return assig
