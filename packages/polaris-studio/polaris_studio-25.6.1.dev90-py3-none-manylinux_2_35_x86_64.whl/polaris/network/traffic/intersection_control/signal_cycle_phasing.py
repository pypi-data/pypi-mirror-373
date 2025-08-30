# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from logging import DEBUG
from sqlite3 import Connection
from typing import List, Dict
from uuid import uuid4

import numpy as np
import pandas as pd

from polaris.network.starts_logging import logger
from polaris.network.traffic.hand_of_driving import DrivingSide

PERMITTED = "PERMITTED"
PROTECTED = "PROTECTED"
STOP_PERMIT = "STOP_PERMIT"


class SignalCyclePhasing:
    """All the information on phasing for one signal cycle"""

    def __init__(self, signal: int, phasing: int, signal_record, conn: sqlite3.Connection):
        from polaris.network.traffic.intersec import Intersection

        self._intersection: Intersection = signal_record.intersection
        self.__signal = signal
        self.__directions: Dict[int, float] = {}
        self.__link_ranks: Dict[int, float] = {}
        self.phases = []  # type: List[pd.DataFrame]
        self.nested_records = pd.DataFrame([])
        self.records = pd.DataFrame([])
        self.phasing = phasing
        self.timing_proportion: List[float] = []
        self.turn_on_red = signal_record.turn_on_red
        self.__id = uuid4().hex
        self.__connections = self._intersection.connections(conn).drop_duplicates(["link", "to_link"])
        self.driving_side = signal_record.intersection.driving_side

        sql = "Select phasing_id from Phasing where signal=? and phasing=?"

        dt = conn.execute(sql, [signal, phasing]).fetchall()
        if len(dt) == 0:
            sql = "PRAGMA table_info(Phasing_Nested_Records);"

            self.nested_records = pd.DataFrame({x[1]: [] for x in conn.execute(sql).fetchall()})
            self.__column_order = list(self.nested_records.columns)
            return
        else:
            for x in dt:
                df = pd.read_sql_query(f"Select * from Phasing_Nested_Records where object_id={x[0]}", conn)
                self.phases.append(df)
            self.__column_order = list(df.columns)
        self.__update_phasing_table()

    def list_movements(self) -> pd.DataFrame:
        """Returns a Pandas Dataframe with all turns listed in one or more phases in this signal"""
        df = self.nested_records[["value_link", "value_to_link"]]
        return df.drop_duplicates()

    def recompute(self, conn: sqlite3.Connection):  # noqa: C901
        """Recomputes the phases based on a list of connections"""

        self.timing_proportion.clear()
        node_links = self._intersection.links(conn)
        self.__directions = node_links[["link", "direction"]].set_index("link").to_dict()["direction"]
        self.__link_ranks = node_links[["link", "link_rank"]].set_index("link").to_dict()["link_rank"]

        unique_links = list(self.__connections.link.unique())
        arrivals = len(unique_links)

        approx_directions = [self.__directions[link] for link in unique_links]
        if len(set(approx_directions)) != len(approx_directions):
            # Different approximations have the same direction (acute angles), and we don't
            # know how to treat that
            arrivals = 5

        phases = []

        self.timing_proportion.clear()
        self.__phase_index = 1
        if arrivals == 1:
            # SHOULD NOT HAVE A TRAFFIC LIGHT
            raise Exception(f"Node {self.__signal} has only one incoming approximation. A traffic light makes no sense")

        elif arrivals == 2:
            # We have exactly two approximations
            for link in unique_links:
                self.timing_proportion.append(self.__link_ranks[link])
                df = self.__connections[self.__connections.link == link]
                df = df.assign(protection=PROTECTED)
                phases.extend(self.__create_movements_for_phase(df))
                self.__phase_index += 1

            # Split equally if both same side of 40 and 70:30 in favour of smaller proportion otherwise
            if min(self.timing_proportion) > 40 or max(self.timing_proportion) <= 40:
                self.timing_proportion = [0.5, 0.5]
            else:
                self.timing_proportion = [0.3, 0.7] if self.timing_proportion[0] > 40 else [0.7, 0.3]

        elif arrivals == 3:
            # we determine the one that has no opposing approximation
            key = list({"EB", "WB", "NB", "SB"} - {str(x) for x in approx_directions})[0]
            reverse = {"EB": "WB", "NB": "SB", "WB": "EB", "SB": "NB"}
            solo = self.__connections.link.unique()
            solo = node_links[node_links.link.isin(solo)]
            solo = solo.loc[solo.direction == reverse[key], "link"].values[0]

            # First phase will be the unimpeded one
            d = self.__directions[solo]
            df = self.__connections[self.__connections.link == solo]
            self.timing_proportion.append(self.__link_ranks[solo])

            df = df.assign(protection=PROTECTED)
            phases.extend(self.__create_movements_for_phase(df))

            unique_links.remove(solo)
            full_df = self.__connections[self.__connections.link != solo]

            # UTurns and turning across signal (e.g. Left with right-hand drive) would cause conflict
            crit1 = full_df.type.isin(["UTURN", self.driving_side.other().long_name()]).any()
            crit2 = full_df.shape[0] - full_df.to_link.unique().shape[0]
            could_conflict = crit1 + crit2

            self.__phase_index = 2
            if not could_conflict:
                self.timing_proportion.append(min([self.__link_ranks[x] for x in unique_links]))
                curr_links = []
                for tp in ["THRU", self.driving_side.long_name()]:
                    for _, row in full_df.loc[full_df["type"] == tp, :].iterrows():
                        use_type = PROTECTED
                        if row["to_link"] in curr_links:
                            use_type = PERMITTED
                        conv = f'{self.__directions[row["link"]]}_{row["type"]}'
                        phases.append([self.__phase_index, -1, conv, row["link"], row["dir"], row["to_link"], use_type])
                        curr_links.append(row["to_link"])
                self.__phase_index += 1
            else:
                phases.extend(self.__phases_for_opposing_movements(full_df))

        elif arrivals == 4:
            # We get the pairs of opposing approximations
            north_south = node_links.loc[node_links.direction.isin(["NB", "SB"]), "link"].values
            east_west = node_links.loc[node_links.direction.isin(["EB", "WB"]), "link"].values

            # And the connections for them
            for pair in [north_south, east_west]:
                full_df = self.__connections[self.__connections.link.isin(pair)]
                phases.extend(self.__phases_for_opposing_movements(full_df))

        else:
            # One phase for each
            self.timing_proportion = [1.0 / len(unique_links)] * len(unique_links)

            for i, link in enumerate(unique_links):
                if self.__link_ranks[link] <= 40:
                    self.timing_proportion[i] *= 2
                df = self.__connections[self.__connections.link == link]
                df = df.assign(protection=PROTECTED)
                dt = self.__create_movements_for_phase(df)
                phases.extend(dt)
                self.__phase_index += 1

        if logger.level == DEBUG:
            logger.debug(f"Phases computed. {self.__id}. Records per phase: {[len(phase) for phase in phases]}")

        tot = sum(self.timing_proportion)
        if tot > 1:
            self.timing_proportion = [x / tot for x in self.timing_proportion]

        if logger.level == DEBUG:
            logger.debug(f" {self.__id}. Timing proportions computed: {self.timing_proportion}")

        cols = ["object_id", "index", "value_movement", "value_link", "value_dir", "value_to_link", "value_protect"]

        # Adds turn-on-red (e.g. turning right with right hand drive)
        if self.turn_on_red:
            if logger.level == DEBUG:
                logger.debug("Adding turn-on-red")

            side_df = self.__connections[self.__connections["type"] == self.driving_side]
            has_side: Dict[int, List[str]] = {int(i): [] for i in range(self.__phase_index)}
            for phase in phases:
                if self.driving_side.long_name() in phase[2]:
                    has_side[phase[0]].append(f"{phase[3]}-{phase[5]}")

            ph = pd.DataFrame(phases, columns=cols)

            for _, row in side_df.iterrows():
                for p in range(1, self.__phase_index):
                    if f"{row.link}-{row.to_link}" in has_side[p]:
                        continue

                    if (
                        ph.loc[
                            (ph.value_protect == STOP_PERMIT) & (ph.value_to_link == row.to_link) & (ph.object_id == p),
                            :,
                        ].shape[0]
                        > 0
                    ):
                        # too many conversions to the same link and with the same hierarchy
                        continue

                    d = self.__directions[row.link]
                    side_phase = [
                        p,
                        -1,
                        f"{d}_" + self.driving_side.long_name(),
                        row.link,
                        row.dir,
                        row.to_link,
                        STOP_PERMIT,
                    ]
                    if side_phase not in phases:
                        phases.append(side_phase)
                        ph = pd.DataFrame(phases, columns=cols)

        if logger.level == DEBUG:
            logger.debug(f"Phases completed. {self.__id}. Records per fase: {[len(phase) for phase in phases]}")

        self.phases.clear()

        if self.__phase_index < 2:
            logger.debug(f"Signal record with less than 2 phases. {self.__id}")

        non_existing = 0
        for k in range(1, self.__phase_index):
            phase_records = [x for x in phases if x[0] == k]
            if not phase_records:
                non_existing += 1
                continue
            df = pd.DataFrame(phase_records, columns=cols)
            df.object_id -= non_existing
            self.phases.append(df)
            if logger.level == DEBUG:
                logger.debug(f"Phases compiled in data frame. {self.__id}. Records: {df.shape[0]}")

        self.__update_phasing_table()

    def save(self, conn: Connection):
        if logger.level == DEBUG:
            logger.debug(f"Saving signal record. {self.__id}")

        self.records.to_sql("Phasing", conn, if_exists="append", index=False)
        self.nested_records.to_sql("Phasing_Nested_Records", conn, if_exists="append", index=False)

    @property
    def data(self) -> dict:
        return {"Phasing": self.records, "Phasing_Nested_Records": self.nested_records}

    def __phases_for_opposing_movements(self, full_df: pd.DataFrame) -> list:
        unique_links = list(full_df.link.unique())
        if len(unique_links) != 2:
            raise Exception("We were supposed to be analysing opposing flows")

        # Find all turns which could conflict:
        conflict_turns = ["UTURN", self.driving_side.other().long_name()]
        could_conflict = full_df.type.isin(conflict_turns).any()

        phases = []
        if not could_conflict:
            curr_links = []
            for tp in ["THRU", self.driving_side.long_name()]:
                for _, row in full_df.loc[full_df["type"] == tp, :].iterrows():
                    use_type = PROTECTED
                    if row["to_link"] in curr_links:
                        use_type = PERMITTED
                    conv = f'{self.__directions[row["link"]]}_{row["type"]}'
                    phases.append([self.__phase_index, -1, conv, row["link"], row["dir"], row["to_link"], use_type])
                    curr_links.append(row["to_link"])
            self.timing_proportion.append(min([self.__link_ranks[x] for x in full_df.link.values]))
            self.__phase_index += 1
        else:  # Deal with conflicting turns:
            problem_link = full_df[full_df.type.isin(conflict_turns)].link.values[0]  # type: ignore
            unique_links.remove(problem_link)
            second_link = unique_links[0]

            conflicting = full_df[full_df.type.isin(conflict_turns)]
            conflicting = conflicting.assign(protection=PROTECTED)
            self.__phases_for_best_protection(conflicting)
            phases.extend(self.__create_movements_for_phase(conflicting))
            # Should be close to 6s
            self.timing_proportion.append(3 * self.__link_ranks[problem_link] / 19)  # type: ignore
            self.__phase_index += 1

            conflicting.loc[:, "protection"] = PERMITTED
            not_conflicting = full_df[~full_df.type.isin(conflict_turns)]
            not_conflicting = not_conflicting.assign(protection=PROTECTED)
            df = pd.concat([not_conflicting, conflicting])

            self.__phases_for_best_protection(df)
            phases.extend(self.__create_movements_for_phase(df))
            self.timing_proportion.append(self.__link_ranks[second_link])
            self.__phase_index += 1

        return phases

    def __phases_for_best_protection(self, df):
        hierarchies = {}
        best_h = [PROTECTED, PERMITTED, STOP_PERMIT]
        tps = (
            ["THRU"] + (["RIGHT", "LEFT"] if self.driving_side == DrivingSide.RIGHT else ["LEFT", "RIGHT"]) + ["UTURN"]
        )
        for tp in tps:
            df2 = df.loc[df.type == tp, :]
            for idx, row in df2.iterrows():
                h = hierarchies.get(row.to_link, 0)
                df.loc[idx, "protection"] = best_h[h]
                hierarchies[row.to_link] = h + 1

    def __create_movements_for_phase(self, df) -> list:
        phases = []
        for _, row in df.iterrows():
            conv = f'{self.__directions[row["link"]]}_{row["type"]}'
            phases.append([self.__phase_index, -1, conv] + list(row[["link", "dir", "to_link", "protection"]].values))
        return phases

    def __update_phasing_table(self):
        id_stack = self.__signal * 100 + self.phasing * 10

        data = []
        for recs in self.phases:
            ph = recs.object_id.values[0]
            data.append([id_stack + ph, self.__signal, self.phasing, ph, recs.shape[0]])
            recs["index"] = np.arange(recs.shape[0])

        cols = ["phasing_id", "signal", "phasing", "phase", "movements"]
        self.records = pd.DataFrame(data, columns=cols)

        self.nested_records = pd.concat(self.phases)
        self.nested_records.object_id += id_stack

        if logger.level == DEBUG:
            logger.debug(f"Phase records compiled as dataframe. Records {self.records.shape[0]}")
            logger.debug(f"Nested records prepared. Records {self.nested_records.shape[0]}")
