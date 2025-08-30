# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from typing import List

from polaris.network.traffic.intersection.approximation import Approximation
from polaris.network.traffic.intersection.connectionrecord import ConnectionRecord
from polaris.network.traffic.intersection.intersecsuperclass import IntersecSuperClass
from polaris.network.traffic.intersection.lane_allocation import lane_allocation
from polaris.network.traffic.intersection.lane_out_direc import adds_pockets_for_approximation
from polaris.network.traffic.intersection.should_allow import should_allow


class GenericIntersection(IntersecSuperClass):
    """Computes the connections for generic intersections

    These intersections are all those not falling within any of the special cases.
    Please check the corresponding documentation for algorithm/logic details

    In the process of processing the intersection, approximations are changed in order
    to consider the pockets necessary.

    This class is not intended to be used independently, but one could do that:

    ::

       from polaris.network.network import Network
       from polaris.network.consistency.network_objects.intersection.regular_intersection_connection import GenericIntersection

       net = Network()
       net.open(connection_test_file)
       i = net.get_intersection(1)
       regular = GenericIntersection(i)

       connections = regular.build()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build(self, conn: sqlite3.Connection) -> List[ConnectionRecord]:
        self.__assess_pocket_needs(conn)

        for inc in self.inter.incoming:  # type: Approximation
            inc._reset_used_connections()

            # Get the allowed departures and sort them
            allowed = self.__allowed_movements(inc)
            if not len(allowed):
                # If there are no allowed movements, this incoming link would be left disconnected
                # To avoid this, we will connect it to the outgoing link with the largest angle difference
                # This is a heuristic needed in corner cases, particular in freeways and frontage roads
                # on the edge of models where we just mangle all links onto a single end node
                differences = [abs(180 - abs(inc.bearing - out.bearing)) for out in self.inter.outgoing]
                idmax = differences.index(max(differences))
                allowed = [self.inter.outgoing[idmax]]

            deps = sorted(allowed + [inc])

            # Cyclically shift the departures about the first incoming link (and drop this link)
            position = [i for i, approx in enumerate(deps) if approx.function == "incoming"][0]
            departures = deps[position + 1 :] + deps[:position]

            # Recreate the connections from the incoming link to each outgoing link
            for approx in departures:
                approx._reset_used_connections()
            self.__one_to_many(inc, departures)

        for out in self.inter.outgoing:
            if out.connected:
                continue
            # If an outgoing link is not connected, then we connect it with the most likely candidate, which is the one
            # with the largest angle difference away from a 180-degree angle
            differences = [abs(180 - abs(out.bearing - inc.bearing)) for inc in self.inter.incoming]
            idmax = differences.index(max(differences))
            inc = self.inter.incoming[idmax]
            self.__one_to_many(inc, [out])

        self._reassess_pocket_needs()
        return self.connects

    def __assess_pocket_needs(self, conn):
        """ """
        for inc in self.inter.incoming:
            departures = self.__allowed_movements(inc)
            adds_pockets_for_approximation(inc, departures, conn)

    def __one_to_many(self, inc: Approximation, departures: List[Approximation]):
        self._compute_balance()
        allocation = lane_allocation(inc, departures)

        for out, alloc in zip(departures, allocation):
            out.connected = True
            lanes = inc.where_to_connect(int(max(1, alloc)))
            inc.mark_used(int(alloc))

            lanes_to_string = out.where_to_connect(out.total_lanes())
            out.mark_used(out.total_lanes())

            con = ConnectionRecord(inc, out, lanes=lanes, to_lanes=lanes_to_string)
            self.connects.append(con)

    def __allowed_movements(self, inc: Approximation) -> List[Approximation]:
        """Returns the allowed outgoing links from the incoming link"""
        return [out for out in self.inter.outgoing if should_allow(self.inter, inc, out)]
