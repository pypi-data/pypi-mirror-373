# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from .approximation import Approximation


def turn_type(inc: Approximation, out: Approximation) -> str:
    """
    Determines the type of turn from inc to out, based on the angle between the two approximations.
    """
    # Get the angle between the two approximations (in range 0-360 degrees)
    delta = (out.bearing - inc.bearing) - 180
    while delta < 0:
        delta += 360

    if delta >= 315 or delta <= 45:
        return "UTURN"
    elif 135 < delta < 225:
        return "THRU"
    elif 45 < delta <= 135:
        return "LEFT"
    return "RIGHT"
