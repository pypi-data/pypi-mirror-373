# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path
import pandas as pd
from polaris.utils.database.db_utils import commit_and_close, count_table, drop_table, filename_from_conn, has_table


def move_table_to_other_db(conn, table_name, db_from, db_to):
    if not has_table(conn, table_name):
        return

    other_db = str(filename_from_conn(conn)).replace(db_from, db_to)

    if not Path(other_db).exists():
        logging.warning(f"Couldn't find a {db_to} database to move your {table_name} data to")
        drop_table(conn, table_name)
        return

    with commit_and_close(other_db) as f_conn:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        if df.shape[0] == 0:
            print(f"Attempting to copy {table_name} data from {db_from}->{db_to}, but table is empty")
            drop_table(conn, table_name)
            return

        if has_table(f_conn, table_name) and count_table(f_conn, table_name) > 0:
            logging.warning(f"Dropping {table_name}, but table exists and has data in {db_to}, not overwriting")
            drop_table(conn, table_name)
            return

        df.to_sql(table_name, f_conn, if_exists="append", index=False)
