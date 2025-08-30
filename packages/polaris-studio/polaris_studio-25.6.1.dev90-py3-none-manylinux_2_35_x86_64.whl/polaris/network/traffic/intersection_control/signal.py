# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
import time
from logging import DEBUG
from typing import Any, Dict

import pandas as pd
from polaris.network.starts_logging import logger
from .signal_record import SignalRecord


class Signal:
    # default_periods = [[0, 21600], [21600, 34200], [34200, 57600], [57600, 68400], [68400, 86400]]
    default_periods = [[0, 86400]]

    def __init__(self, intersection, conn: sqlite3.Connection):
        from polaris.network.traffic.intersec import Intersection

        if intersection is None:
            return
        self._inter: Intersection = intersection
        self._data_tables = intersection._data
        self.turn_on_red = True  # E.g. turning right at signal for right-hand drive
        self.__bulk_loading__ = False

        # We load the signal table as records of itself
        df = self._data_tables.get("signal", conn=conn, from_cache_ok=True)  # type: pd.DataFrame
        names = [str(x) for x in list(df.columns)]
        sig_rec = df[df.nodes == intersection.node]

        if sig_rec.empty:
            for title in names:
                self.__dict__[title] = -1
            # No signal to load
            self.signal = intersection.node
            self.nodes = intersection.node
            self.group = 1
            self.offset = 0
            self.times = 0
            self.type = "TIMED"
            self.records = []
            return

        self.signal = sig_rec.index[0]
        for title in names:
            self.__dict__[title] = sig_rec[title].values[0]

        snr = self._data_tables.get("signal_nested_records", conn=conn, from_cache_ok=True)  # type: pd.DataFrame
        sig_nested = snr[snr.object_id == self.signal]

        self.records = [SignalRecord(record.to_dict(), self, conn) for _, record in sig_nested.iterrows()]

    def delete(self, conn: sqlite3.Connection):
        """Removes signal from database"""

        conn.execute("Delete from  Signal where nodes=?", [self.nodes])
        conn.commit()

    def re_compute(self, conn: sqlite3.Connection):
        self.records = []
        logger.debug(f"Recomputing signal for node {self.nodes}")
        for start_, end_ in self.default_periods:
            logger.debug(f"Adding period {str(start_)}-{str(end_)} to signal")
            self.add_period(start_, end_, conn)

    def add_period(self, value_start: int, value_end: int, conn: sqlite3.Connection):
        """Adds a period record to this signal

        Args:
            *value_start* (:obj:`int`): The second this period goes from (0 to 86400). Must be a whole minute

            *value_end* (:obj:`int`): The second this period goes from (0 to 86400). Must be a whole minute and larger than value_start
        """

        timing = phasing = len(self.records) + 1

        sig_nested: pd.DataFrame = self._data_tables.get("signal_nested_records", conn=conn, from_cache_ok=True)
        record: Dict[str, Any] = {str(field): None for field in sig_nested.columns}

        if value_start >= value_end:
            raise ValueError("value_end must be smaller than value_start")

        if value_start < 0:
            raise ValueError("value_start must be positive")

        if value_end > 86400:
            raise ValueError("value_end must be no larger than 86,400")

        def convert(val):
            if val == 86400:
                return "24:00"
            return time.strftime("%H:%M", time.gmtime(val))

        record["value_start"] = convert(value_start)
        record["value_end"] = convert(value_end)
        record["object_id"] = self.signal
        record["value_timing"] = timing
        record["value_phasing"] = phasing

        if logger.level == DEBUG:
            logger.debug(f"    Records computed: {record}")

        sr = SignalRecord(record, self, conn)

        self.records.append(sr)
        self.times = len(self.records)

        sr.compute_phasing(conn)

    def save(self, conn: sqlite3.Connection):
        """Saves traffic signal to the network file"""
        logger.info(f"Signal data saved for node {self._inter.node}")
        self.delete(conn)

        data = self.data["Signal"]
        data.to_sql("Signal", conn, if_exists="append", index=False)
        for record in self.records:
            record.save(conn)
        conn.commit()

        self.__refresh_tables()

    @property
    def data(self) -> dict:
        df = pd.DataFrame(
            [[int(self.nodes), int(self.group), 0, int(self.nodes), str(self.type), int(self.offset)]],
            columns=["signal", "group", "times", "nodes", "type", "offset"],
        )

        dt = {"Signal": df}
        for record in self.records:
            rec_dt = record.data
            for tb in ["Signal_Nested_Records", "Phasing", "Phasing_Nested_Records", "Timing", "Timing_Nested_Records"]:
                # If one is empty, it will be the first one, as for a single signal all records would be filled
                if tb not in dt or dt[tb] is None or dt[tb].empty:
                    dt[tb] = rec_dt[tb]
                else:
                    dt[tb] = pd.concat([dt[tb], rec_dt[tb]])
        return dt

    def __refresh_tables(self):
        if self.__bulk_loading__:
            return
        for tn in [
            "Timing",
            "Timing_Nested_Records",
            "Phasing",
            "Phasing_Nested_Records",
            "Signal",
            "Signal_nested_Records",
        ]:
            self._data_tables.refresh_cache(tn)
