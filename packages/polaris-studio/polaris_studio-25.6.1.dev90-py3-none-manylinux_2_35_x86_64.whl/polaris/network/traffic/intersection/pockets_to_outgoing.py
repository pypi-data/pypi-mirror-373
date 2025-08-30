# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from sqlite3 import Connection
from typing import List

from polaris.network.traffic.hand_of_driving import DrivingSide
from polaris.network.traffic.intersection.approximation import Approximation
from polaris.network.traffic.intersection.turn_type import turn_type


def pockets_to_out_link(inc: Approximation, outgoing: List[Approximation], lane_balance, supply_conn: Connection):
    balance = movements_per_direction(inc, outgoing)

    sequence = (
        balance["RIGHT"] + balance["LEFT"]
        if inc.driving_side == DrivingSide.RIGHT
        else balance["LEFT"] + balance["RIGHT"]
    )

    for out in sequence:  # type: Approximation
        lane_balance -= 1
        if out in balance["RIGHT"]:
            out._l_pckts = 1
        else:
            out._r_pckts = 1

        if lane_balance == 0:
            return


def movements_per_direction(inc, outgoing):
    """
    For each outgoing link determines which type of turn it is, and return these as a dictionary
    """
    # Side turns would always come primarily from pockets, but we need to know how many turns to each side
    balance = {"LEFT": [], "RIGHT": [], "THRU": [], "UTURN": []}
    for out in outgoing:
        balance[turn_type(inc, out)].append(out)

    # UTURN's requires additional pockets on the relevant side
    balance[inc.driving_side.other().long_name()].extend(balance["UTURN"])
    return balance
