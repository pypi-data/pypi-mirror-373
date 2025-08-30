# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import List

import numpy as np

from polaris.network.traffic.intersection.approximation import Approximation


def lane_allocation(single_approx: Approximation, list_approx: List[Approximation]):
    target_total = single_approx.total_lanes()
    if len(list_approx) <= 1:
        return [target_total]
    ideal_target = sum([approx.total_lanes() for approx in list_approx])

    allocation = [approx.total_lanes() * target_total / ideal_target for approx in list_approx]
    cummul_allocs = np.floor(np.cumsum(allocation))
    cummulative = [cummul_allocs[0]] + list(cummul_allocs[1:] - cummul_allocs[:1])
    guaranteed_cummulative = [x if x < target_total else x - 1 for x in cummulative]
    guaranteed_cummulative[-1] = target_total
    return guaranteed_cummulative
