# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import pandas as pd
import shapely.wkb
from shapely.geometry import LineString

from .find_directions import find_directions
from polaris.network.traffic.hand_of_driving import DrivingSide

pocket_table_fields = ["link", "dir", "node", "type", "lanes", "length"]


class Approximation:
    """A link connecting to a node

    ::

        from polaris.network.network import Network

        net = Network()
        net.open('D:/Argonne/GTFS/CHICAGO/chicago2018-Supply.sqlite')
        intersection = net.get_intersection(2468)

        # List of all links that "Arrive in the node"
        intersection.incoming

        # List of all links that "depart from the node"
        intersection.outgoing

        # One can manipulate the possibility of approximations to have
        # pockets added when building connections based on link IDs
        # doing the following:

        for approx in intersection.incoming:
            if approx.link == 12345:
                approx.set_allow_pockets()

            if approx.link == 67890:
                approx.set_block_pockets()
    """

    #: Maximum pocket length
    max_pocket = 400
    pocket_insert_sql = "INSERT INTO Pocket(link,dir,type,lanes,length) VALUES(?,?,?,?,?)"
    pocket_table_fields = pocket_table_fields

    def __init__(self, data: list, driving_side=DrivingSide.RIGHT) -> None:
        self.node: int = data[0]
        self.link: int = data[1]
        self.lanes: int = data[2]
        self.geo: LineString = shapely.wkb.loads(data[3])
        self.link_rank: int = data[4]
        self.allows_pockets = data[5] > 0
        self.direction: int = data[6]
        self.function = data[7].lower()
        self.bearing: float = data[8] % 360
        self.pocket_length: float = min(max(round(0.15 * self.geo.length, 0), 10), self.max_pocket)
        self.connected = False

        # If the field is not filled, then we allow for pockets
        self.cardinal: str = find_directions(self.bearing)

        # These parameters are designed to be changed as a function of the other approximation it is compared to
        self.penalty = 0
        self._r_pckts: int = 0
        self._l_pckts: int = 0
        self.__used_l_pckts: int = 0
        self.__used_r_pckts: int = 0
        self._used_lanes: int = 0
        self._current_lane_to_use: int = 1
        self.driving_side: DrivingSide = driving_side

    # To avoid rewriting and possibly breaking the existing logic we'll use "slow" and "fast" lanes to denote the
    # lane ordering on different driving sides and getters and setters to enforce conformity
    @property
    def slow_pockets(self):
        return self._r_pckts if self.driving_side == DrivingSide.RIGHT else self._l_pckts

    @slow_pockets.setter
    def slow_pockets(self, val):
        if self.driving_side == DrivingSide.RIGHT:
            self._r_pckts = val
        else:
            self._l_pckts = val

    @property
    def fast_pockets(self):
        return self._l_pckts if self.driving_side == DrivingSide.RIGHT else self._r_pckts

    @fast_pockets.setter
    def fast_pockets(self, val):
        if self.driving_side == DrivingSide.RIGHT:
            self._l_pckts = val
        else:
            self._r_pckts = val

    @property
    def used_slow_pockets(self):
        return self.__used_r_pckts if self.driving_side == DrivingSide.RIGHT else self.__used_l_pckts

    @used_slow_pockets.setter
    def used_slow_pockets(self, val):
        if self.driving_side == DrivingSide.RIGHT:
            self.__used_r_pckts = val
        else:
            self.__used_l_pckts = val

    @property
    def used_fast_pockets(self):
        return self.__used_l_pckts if self.driving_side == DrivingSide.RIGHT else self.__used_r_pckts

    @used_fast_pockets.setter
    def used_fast_pockets(self, val):
        if self.driving_side == DrivingSide.RIGHT:
            self.__used_l_pckts = val
        else:
            self.__used_r_pckts = val

    def set_allow_pockets(self):
        """Allows pockets to be built for this link"""
        self.allows_pockets = True

    def set_block_pockets(self):
        """Prevents pockets to be built for this link"""
        self.allows_pockets = False

    @property
    def pocket_data(self) -> pd.DataFrame:
        pckt = "MERGE" if self.function == "outgoing" else "TURN"
        dt = [[self._l_pckts, "LEFT"], [self._r_pckts, "RIGHT"]]
        dt = [[self.link, self.direction, self.node, f"{direc}_{pckt}", e, self.pocket_length] for e, direc in dt if e]
        return pd.DataFrame(dt, columns=pocket_table_fields)

    @property
    def has_pockets(self) -> bool:
        return self._r_pckts > 0 or self._l_pckts > 0

    def where_to_connect(self, num_lanes: int) -> str:
        assert num_lanes > 0

        fulfilled = 0
        res_str = ""
        if self.slow_pockets > self.used_slow_pockets:
            res_str += f",{self.driving_side}1"
            fulfilled += 1
        if fulfilled < num_lanes and self.lanes - self._used_lanes > 0:
            lanes = min(self.lanes - self._used_lanes, num_lanes - fulfilled)
            res_str += "," + ",".join([str(x + self._used_lanes + 1) for x in range(lanes)])
            fulfilled += lanes
        if fulfilled < num_lanes and self.fast_pockets > self.used_fast_pockets:
            res_str += f",{self.driving_side.other()}1"

        return res_str[1:]

    def mark_used(self, tot_lanes):
        """Marks a set of lanes as having been already connected"""
        used_lanes = self.used_slow_pockets + self.used_fast_pockets + self._used_lanes
        assigned = tot_lanes - used_lanes

        if self.used_slow_pockets < self.slow_pockets and assigned > 0:
            pockets = min(assigned, self.slow_pockets - self.used_slow_pockets)
            self.used_slow_pockets = pockets
            assigned -= pockets

        if assigned > 0:
            lanes = min(assigned, self.lanes - self._used_lanes)
            self._used_lanes += lanes
            assigned -= lanes

        if assigned > 0:
            self.used_fast_pockets = min(assigned, self.fast_pockets - self.used_fast_pockets)

    def total_lanes(self) -> int:
        """Returns all lanes this link has in the intersection"""
        return self.lanes + self._r_pckts + self._l_pckts

    def is_ramp(self):
        """Returns True if link is a Ramp and False otherwise"""
        return self.link_rank == 100

    def _reset_used_connections(self):
        self.__used_l_pckts = 0
        self.__used_r_pckts = 0
        self._current_lane_to_use = 1
        self._used_lanes = 0

    def __lt__(self, other):
        return self.bearing < other.bearing

    def __radd__(self, other):
        return other + self.lanes + self._r_pckts + self._l_pckts
