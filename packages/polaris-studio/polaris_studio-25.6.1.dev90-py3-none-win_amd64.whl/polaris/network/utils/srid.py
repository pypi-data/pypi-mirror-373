# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
# Copied from AequilibraE
import os
import sqlite3
from typing import Optional

import numpy as np

from polaris.utils.database.db_utils import read_and_close

sqlite3.register_adapter(np.int64, int)
sqlite3.register_adapter(np.int32, int)
sqlite3.register_adapter(np.float32, float)
sqlite3.register_adapter(np.float64, float)
sqlite3.register_adapter(object, str)


def get_srid(
    database_path: Optional[os.PathLike] = None, conn: Optional[sqlite3.Connection] = None, freight=False
) -> int:
    if database_path is None and conn is None:
        raise Exception("To retrieve an SRID you must provide a database connection OR a path to the database")
    table = "link" if not freight else "airport"
    with conn or read_and_close(database_path) as conn:
        return get_table_srid(conn, table)


def get_table_srid(conn: sqlite3.Connection, table_name) -> int:
    dt = conn.execute(f'select srid from geometry_columns where f_table_name="{table_name.lower()}"').fetchone()
    return int(dt[0]) if dt else -1
