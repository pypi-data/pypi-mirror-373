# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from typing import List

from polaris.network.consistency.link_types_constants import FREEWAY, EXPRESSWAY
from .connectionrecord import ConnectionRecord
from .intersecsuperclass import IntersecSuperClass
from .links_merge import LinksMerge
from .regular_intersection_connection import GenericIntersection
from .should_allow import should_allow
from .turn_type import turn_type


class FreewayIntersection(IntersecSuperClass):
    """Computes the connections for a freeway intersection

    These are a bit different than others because they are basically big merges, most
    often with a single point of entry or exit.  Cases with multiple entries and multiple
    exits are also covered.

    In the process of processing the intersection, approximations are changed in order
    to consider the pockets necessary.

    Please check the corresponding documentation for algorithm/logic details

    This class is not intended to be used independently, but one could do that:

    ::

       from polaris.network.network import Network
       from polaris.network.consistency.network_objects.intersection.freeway_intersection import FreewayIntersection

       net = Network()
       net.open(connection_test_file)
       i = net.get_intersection(1)
       freeway = FreewayIntersection(i)

       connections = freeway.build()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "diverge"
        self.intersection_type = "freeway"
        self.__pockets = ""
        incoming_ramp = sum([x.lanes for x in self.inter.incoming if x.is_ramp()])
        outgoing_ramp = sum([x.lanes for x in self.inter.outgoing if x.is_ramp()])
        if incoming_ramp > outgoing_ramp:
            self.type = "merge"
        self.__preprocess()

    def __preprocess(self):
        self._compute_balance()
        # sets to detect if we have a T-junction
        sets = []
        for inc in self.inter.incoming:
            sets.append({turn_type(inc, out) for out in self.inter.outgoing if should_allow(self.inter, inc, out)})

        must_have_sets = [{"LEFT", "RIGHT"}, {"THRU", "RIGHT"}, {"LEFT", "THRU"}]
        sets = [s in must_have_sets for s in sets]
        lengths = [len(self.inter.incoming), len(self.inter.outgoing)]

        inc_freeway = sum([1 for inc in self.inter.incoming if inc.link_rank in [EXPRESSWAY, FREEWAY]])
        out_freeway = sum([1 for inc in self.inter.outgoing if inc.link_rank in [EXPRESSWAY, FREEWAY]])
        if min(lengths) == 1:
            self.inter.intersection_type = "merge"
        elif all(sets) or min(inc_freeway, out_freeway) > 1:
            self.inter.intersection_type = "generic"

    def build(self, conn: sqlite3.Connection) -> List[ConnectionRecord]:
        if self.inter.intersection_type == "merge":
            return LinksMerge(self.inter).build(conn)

        return GenericIntersection(self.inter).build(conn)
