# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from .approximation import Approximation
from .connectionrecord import ConnectionRecord
from .lane_string import lane_string


def connect_two_links_top_to_top(inc: Approximation, out: Approximation) -> ConnectionRecord:
    con = ConnectionRecord(inc, out)
    con.lanes = lane_string(1, inc.lanes)
    con.to_lanes = lane_string(1, out.lanes)
    return con
