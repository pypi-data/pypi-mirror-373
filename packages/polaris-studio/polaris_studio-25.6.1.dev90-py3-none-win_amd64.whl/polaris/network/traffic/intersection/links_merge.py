# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from typing import List

from polaris.network.traffic.intersection.connectionrecord import ConnectionRecord
from polaris.network.traffic.intersection.intersecsuperclass import IntersecSuperClass
from polaris.network.traffic.intersection.lane_allocation import lane_allocation


class LinksMerge(IntersecSuperClass):
    """Computes the connections for merge intersections

    These intersections are characterized for having either a single point of entry or
    exit, but where at least one link is not in [Freeway, Arterial, Ramp] set.

    In the process of processing the intersection, approximations are changed in order
    to consider the pockets necessary.

    Please check the corresponding documentation for algorithm/logic details

    This class is not intended to be used independently, but one could do that:

    ::

       from polaris.network.network import Network
       from polaris.network.consistency.network_objects.intersection.links_merge import LinksMerge

       net = Network()
       net.open(connection_test_file)
       i = net.get_intersection(1)
       merge = LinksMerge(i)

       connections = merge.build()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._compute_balance()

    def build(self, conn: sqlite3.Connection) -> List[ConnectionRecord]:
        if self.lane_balance != 0:
            self.__attempt_balancing()

        if len(self.inter.incoming) == 1:
            self.__build_split()
        elif len(self.inter.outgoing) == 1:
            self.__build_merge()
        else:
            raise ValueError(f"Node {self.inter.node} is not a merge!")
        self._reassess_pocket_needs()
        return self.connects

    def __attempt_balancing(self):
        if self.lane_balance > 0 and len(self.inter.incoming) > 1:
            # If either the leftmost or rightmost  upstream link has a number of lanes equal or smaller
            # than the lane surplus, we can put pockets downstream that would receive ALL of those lanes
            self._pockets_downstream()

        elif self.lane_balance < 0 and len(self.inter.incoming) == 1:
            # If either the leftmost or rightmost downstream link has a number of lanes equal or smaller
            # than then the lane deficit, then we can put pockets upstream that would connect to that link
            self._pockets_upstream()

    def __build_merge(self):
        out = self.inter.outgoing[0]
        candidates = list(self.inter.incoming)
        allocation = lane_allocation(out, candidates)

        for inc, alloc in zip(candidates, allocation):
            lanes = inc.where_to_connect(inc.total_lanes())
            inc.mark_used(inc.total_lanes())
            lanes_to_string = out.where_to_connect(int(max(1, alloc)))
            out.mark_used(int(alloc))

            con = ConnectionRecord(inc, out, lanes=lanes, to_lanes=lanes_to_string)
            self.connects.append(con)

    def __build_split(self):
        inc = self.inter.incoming[0]
        outgoing = list(self.inter.outgoing)

        allocation = lane_allocation(inc, outgoing)

        for out, alloc in zip(outgoing, allocation):
            lanes = inc.where_to_connect(int(max(1, alloc)))
            inc.mark_used(int(alloc))

            lanes_to_string = out.where_to_connect(out.total_lanes())
            out.mark_used(out.total_lanes())

            con = ConnectionRecord(inc, out, lanes=lanes, to_lanes=lanes_to_string)
            self.connects.append(con)
