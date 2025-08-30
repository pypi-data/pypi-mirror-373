# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import Union


def lane_string(from_lane: Union[int, str], tot_lanes: int) -> str:
    if isinstance(from_lane, int):
        return ",".join([f"{x}" for x in range(from_lane, from_lane + tot_lanes)])
    elif isinstance(from_lane, str):
        pckt, ln = from_lane[0], int(from_lane[1:])
        return ",".join([f"{pckt}{x}" for x in range(ln, ln + tot_lanes)])
    else:
        raise TypeError("from_lane has wrong type")
