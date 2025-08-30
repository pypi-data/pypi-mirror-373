# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from .should_allow import should_allow
from polaris.network.traffic.hand_of_driving import DrivingSide


class IntersecSuperClass:
    def __init__(self, intersection):
        self.inter = intersection  # type: Intersection
        self.connects = []  # type: List[ConnectionRecord]
        self._path_to_file = intersection._path_to_file
        self.lane_balance = 0
        self._compute_balance()
        self.lane_labels = (
            tuple(DrivingSide) if self.inter.driving_side == DrivingSide.RIGHT else tuple(reversed(DrivingSide))
        )

    def _compute_balance(self):
        """Computes the difference in the number of incoming and outgoing lanes"""
        self.lane_balance = sum(self.inter.incoming) - sum(self.inter.outgoing)

    def _pockets_downstream(self):
        candidates = [self.inter.incoming[0], self.inter.incoming[-1]]
        out_candidates = [self.inter.outgoing[0], self.inter.outgoing[-1]]
        sizes = [approx.lanes for approx in candidates]
        candidates = [approx for _, approx in sorted(zip(sizes, candidates), reverse=True)]
        sides = [side for _, side in sorted(zip(sizes, ["R", "L"]), reverse=True)]
        for approx, side, out in zip(candidates, sides, out_candidates):
            possible = [inc for inc in self.inter.incoming if should_allow(self.inter, inc, out)]
            if not should_allow(self.inter, approx, out) or len(possible) < 2:
                continue
            if approx.lanes <= self.lane_balance:
                if side == "L":
                    self.inter.outgoing[self.inter.driving_side.other_index(side)].l_pckts = 1
                else:
                    self.inter.outgoing[self.inter.driving_side.other_index(side)].r_pckts = 1
                self._compute_balance()

    def _pockets_upstream(self):
        candidates = [self.inter.outgoing[0], self.inter.outgoing[-1]]
        inc_candidates = [self.inter.incoming[0], self.inter.incoming[-1]]
        sizes = [approx.lanes for approx in candidates]
        candidates = [approx for _, approx in sorted(zip(sizes, candidates), reverse=True)]
        sides = [side for _, side in sorted(zip(sizes, self.lane_labels), reverse=True)]  # here
        for approx, side, inc in zip(candidates, sides, inc_candidates):
            possible = [out for out in self.inter.outgoing if should_allow(self.inter, inc, out)]
            if not should_allow(self.inter, inc, approx) or len(possible) < 2:
                continue

            if approx.lanes <= abs(self.lane_balance):
                if side == "L":
                    self.inter.incoming[self.inter.driving_side.other_index(side)].l_pckts = 1
                else:
                    self.inter.incoming[self.inter.driving_side.other_index(side)].r_pckts = 1
                self._compute_balance()

    def _reassess_pocket_needs(self):
        """
        Determines the right/left pockets required for each incoming/outgoing link.
        """
        # Determine incoming links and whether they join from the right/left resp.
        # and add pockets if needed
        right_in = [cnn.link for cnn in self.connects if "R" in cnn.lanes]
        left_in = [cnn.link for cnn in self.connects if "L" in cnn.lanes]
        for inc in self.inter.incoming:
            inc.r_pckts = 1 if inc.link in right_in else 0
            inc.l_pckts = 1 if inc.link in left_in else 0

        # Do the same, but for each outgoing link
        right_out = [cnn.to_link for cnn in self.connects if "R" in cnn.to_lanes]
        left_out = [cnn.to_link for cnn in self.connects if "L" in cnn.to_lanes]
        for out in self.inter.outgoing:
            out.r_pckts = 1 if out.link in right_out else 0
            out.l_pckts = 1 if out.link in left_out else 0
