# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3

import pandas as pd

from polaris.utils.database.db_utils import add_column_unless_exists


def add_required_fields(df: pd.DataFrame, table_name: str, conn: sqlite3.Connection):
    schema = pd.read_sql_query(f'pragma table_info("{table_name}")', conn)

    schema["dflt_value"] = schema.dflt_value.str.replace("['\"]", "", regex=True)
    for _, rec in schema.iterrows():
        if not rec.notnull or "geo" in rec["name"]:  # type: ignore
            continue
        if rec["name"] not in df:
            df[rec["name"]] = rec.dflt_value
        elif rec.dflt_value:
            if df[rec["name"]].dtype.kind == "f":
                val = float(rec.dflt_value) if len(rec.dflt_value) > 0 else 0
            else:
                val = rec.dflt_value
            df[rec["name"]] = df[rec["name"]].fillna(value=val)

    for column in [str(x) for x in df.columns]:
        if column == "geo":
            continue
        data_type = "INTEGER" if df[column].dtype.kind == "i" else "TEXT"
        data_type = "NUMERIC" if df[column].dtype.kind == "f" else data_type
        add_column_unless_exists(conn, table_name, column, data_type)
