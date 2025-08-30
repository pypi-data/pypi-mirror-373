# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

import pandas as pd

from polaris.utils.database.db_utils import has_table, run_sql_file


def migrate(conn):
    if has_table(conn, "Transit_Modes"):
        return
    sql_file = Path(__file__).absolute().parent.parent / "sql_schema" / "transit_modes.sql"
    csv_file = Path(__file__).absolute().parent.parent / "default_values" / "Transit_Modes.csv"
    run_sql_file(sql_file, conn)
    pd.read_csv(csv_file).to_sql("Transit_Modes", conn, if_exists="append", index=False)
