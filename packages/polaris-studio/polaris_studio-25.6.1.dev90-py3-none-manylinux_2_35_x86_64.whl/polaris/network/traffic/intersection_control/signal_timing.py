# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from logging import DEBUG
from sqlite3 import Connection
from typing import Dict, List, Any
from uuid import uuid4

import pandas as pd
from polaris.network.starts_logging import logger


class SignalTiming:
    min_green = 6

    def __init__(self, signal: int, timing: int, signal_record, conn: sqlite3.Connection):
        self.signal_record = signal_record
        self.signal = signal
        self.timing = timing
        self.timing_id = signal * 10 + timing
        self.type = "TIMED"
        self.cycle = -1
        self.offset = 0
        self.phases = -1

        dt = conn.execute("Select timing_id from Timing where signal=? and timing=?", [signal, timing]).fetchone()
        self.__id = uuid4().hex
        if dt is None:
            sql = "PRAGMA table_info(Timing_Nested_Records);"

            empty_shell: Dict[int, List[Any]] = {x[1]: [] for x in conn.execute(sql).fetchall()}
            self.timing_records = pd.DataFrame(empty_shell)
        else:
            if self.timing_id != dt[0]:
                raise Exception("timing_id is not according to the standard")
            df = pd.read_sql_query(f"Select * from Timing_Nested_Records where object_id={self.timing_id}", conn)
            self.timing_records = df

        self.__column_order = list(self.timing_records.columns)

    def compute_timing(self):
        if not self.timing_records.empty:
            raise Exception("Remove records before recomputing")
        phase_records = self.signal_record.phasing.records  # type: SignalCyclePhasing
        times = [int(x * self.cycle) for x in self.signal_record.phasing.timing_proportion]

        record = {"object_id": [self.timing_id], "value_barrier": [1], "value_ring": [1], "value_extend": [0]}

        records = []
        for i, phase in enumerate(phase_records.phase.values):
            record["index"] = [i]
            record["value_phase"] = [phase]
            record["value_position"] = [phase]
            record["value_minimum"] = [times[i]]
            record["value_maximum"] = [times[i]]
            record["value_yellow"] = [0]
            record["value_red"] = [0]
            df = pd.DataFrame.from_dict(record)
            records.append(df)

        self.timing_records = pd.concat(records, ignore_index=True)

        if logger.level == DEBUG:
            logger.debug(f"Timing records assembled. Records: {self.timing_records.shape[0]}")

        movs = self.signal_record.phasing.nested_records
        movs = movs[movs.value_movement.str.contains("THRU")]

        df = self.timing_records
        if movs.shape[0] > 0:
            need_red = movs.groupby(["value_link", "value_to_link"]).max()["object_id"].unique()

            recs = self.signal_record.phasing.records
            phases_with_red = recs[recs.phasing_id.isin(need_red)].phase.to_list()

            df.loc[df.value_phase.isin(phases_with_red), "value_yellow"] = 3
            df.loc[df.value_phase.isin(phases_with_red), "value_red"] = 1
            df.loc[df.value_phase.isin(phases_with_red), ["value_minimum", "value_maximum"]] -= 4

        if df.value_minimum.min() < self.min_green:
            df.loc[df.value_minimum < self.min_green, ["value_minimum", "value_maximum"]] = self.min_green

        tot = df.sum()[["value_yellow", "value_red", "value_minimum"]].sum()

        while tot > self.cycle:
            idx = df[df.value_maximum == df.value_maximum.max()].index[0]
            df.loc[idx, ["value_minimum", "value_maximum"]] -= 1
            tot = df.sum()[["value_yellow", "value_red", "value_minimum"]].sum()

        while tot < self.cycle:
            idx = df[df.value_maximum == df.value_maximum.min()].index[0]
            df.loc[idx, ["value_minimum", "value_maximum"]] += 1
            tot = df.sum()[["value_yellow", "value_red", "value_minimum"]].sum()

        if logger.level == DEBUG:
            logger.debug(f"Values for timing records adjusted. Records: {self.timing_records.shape[0]}")

    def save(self, conn: Connection):
        self.timing_records.to_sql("Timing_Nested_Records", conn, if_exists="append", index=False)
        self.data["Timing"].to_sql("Timing", conn, if_exists="append", index=False)

    @property
    def data(self) -> dict:
        df = pd.DataFrame(
            [[self.timing_id, self.signal, self.timing, self.type, self.cycle, self.offset, self.phases]],
            columns=["timing_id", "signal", "timing", "type", "cycle", "offset", "phases"],
        )
        return {"Timing": df, "Timing_Nested_Records": self.timing_records}
