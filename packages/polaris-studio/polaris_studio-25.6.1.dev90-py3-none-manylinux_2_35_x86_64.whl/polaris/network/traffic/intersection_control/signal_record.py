# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from sqlite3 import Connection

import pandas as pd

from .signal_cycle_phasing import SignalCyclePhasing
from .signal_timing import SignalTiming

MAJOR_INTERSECTION_CYCLE = 90
MINOR_INTERSECTION_CYCLE = 75
MAJOR = 40
PRINCIPAL = 30
EXPRESSWAY = 20
FREEWAY = 10


class SignalRecord:
    save_sql = """Insert into Signal_Nested_Records(object_id, "index", value_start, value_end, value_timing,
                                                    value_phasing) values(?,?,?,?,?,?)"""

    def __init__(self, record: dict, signal, conn: sqlite3.Connection):
        self.value_start = ""
        self.value_end = ""
        self.object_id = -1
        self.value_phasing = -1
        self.value_timing = -1
        self.intersection = signal._inter
        self.turn_on_red = signal.turn_on_red

        for title, value in record.items():
            self.__dict__[title] = value

        if self.value_start:
            h, m = map(int, self.value_start.split(":"))
            self.start = h * 3600 + m * 60

            h, m = map(int, self.value_end.split(":"))
            self.end = h * 3600 + m * 60

        self.phasing = SignalCyclePhasing(self.object_id, self.value_phasing, self, conn)
        self.timing = SignalTiming(self.object_id, self.value_timing, self, conn)
        self.timing.phases = len(self.phasing.phases)
        self.__set_cycle()

    def compute_phasing(self, conn: sqlite3.Connection):
        """Computes phasing and timing for this period"""
        self.phasing.recompute(conn)
        self.timing.phases = len(self.phasing.phases)
        self.timing.compute_timing()

    def save(self, conn: Connection):
        """Saves traffic signal record to database
        Corresponds to a phasing/timing record for one specific time period during the day"""
        for table, df in self.data.items():
            df.to_sql(table, conn, if_exists="append", index=False)

    @property
    def data(self) -> dict:
        df = pd.DataFrame(
            [
                [
                    self.intersection.node,
                    self.value_phasing - 1,
                    self.value_start,
                    self.value_end,
                    self.value_timing,
                    self.value_phasing,
                ]
            ],
            columns=["object_id", "index", "value_start", "value_end", "value_timing", "value_phasing"],
        )

        dt = {"Signal_Nested_Records": df}
        dt.update(self.phasing.data)
        dt.update(self.timing.data)
        return dt

    def __set_cycle(self):
        inc = sum([1 for x in self.intersection.incoming if x.link_rank in [MAJOR, PRINCIPAL, EXPRESSWAY, FREEWAY]])
        out = sum([1 for x in self.intersection.outgoing if x.link_rank in [MAJOR, PRINCIPAL, EXPRESSWAY, FREEWAY]])

        if max(inc, out) > 2:
            self.timing.cycle = MAJOR_INTERSECTION_CYCLE
        else:
            self.timing.cycle = MINOR_INTERSECTION_CYCLE

        # We add an extra 15 seconds for each incoming approximation when there are more than 5 approximations
        if len(self.intersection.incoming) > 5:
            self.timing.cycle += 15 * (len(self.intersection.incoming) - 5)
