# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3

import pandas as pd


def summary(conn: sqlite3.Connection):
    def table_count(name):
        return pd.read_sql(f"SELECT '{name}' as name, COUNT(*) count from {name}", con=conn)

    tables = ["Person", "Household", "Selection", "Person_Gaps", "Activity", "Planned_Activity", "Traveler", "Trip"]
    return pd.concat([table_count(x) for x in tables])
