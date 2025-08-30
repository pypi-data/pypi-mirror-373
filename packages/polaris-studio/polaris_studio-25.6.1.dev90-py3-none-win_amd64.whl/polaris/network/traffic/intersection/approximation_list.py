# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import List, Tuple


from polaris.network.traffic.hand_of_driving import DrivingSide
from polaris.network.traffic.intersection.approximation import Approximation


def sort_approx_list(approximations: List[Approximation]) -> Tuple[List[Approximation], List[Approximation]]:
    """
    Sorts the approximations counter-clockwise around the intersection node, starting
    in the direction such that the difference between each angle and the previous angle
    is minimised.

    Returns the incoming and outgoing approximations in that order.

    The sorted order is reversed if using left-hand drive.
    """
    driving_side = approximations[0].driving_side
    sorted_approx = sorted(approximations)
    thetas = [approx.bearing for approx in sorted_approx]
    diffs = [x - y for x, y in zip(thetas[1:], thetas[:-1])]
    diffs.append(360 + thetas[0] - thetas[-1])  # Add angle from last direction to first

    if driving_side == DrivingSide.RIGHT:
        position = diffs.index(max(diffs)) + 1
    else:
        position = diffs.index(min(diffs))
    sorted_approx = (sorted_approx[position:] + sorted_approx[:position])[::-1]
    incoming = [inc for inc in sorted_approx if inc.function == "incoming"][::-1]
    outgoing = [inc for inc in sorted_approx if inc.function == "outgoing"]
    return incoming, outgoing
