# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from os import PathLike

from polaris.utils.database.data_table_access import DataTableAccess


def add_uses(use_list, conn: sqlite3.Connection, path_to_file: PathLike):
    # Thorough documentation of the assumptions used in this code is provided
    # with the package documentation

    cuc = DataTableAccess(path_to_file).get("Use_Code", conn=conn)

    adds = [use for use in use_list if use not in cuc.use_code.values]
    i = 1 if cuc.empty else cuc["rank"].max() + 1
    data = [[use, i + j, 1] for j, use in enumerate(adds)]

    if not data:
        return

    sql = """INSERT INTO Use_code(use_code, rank, routable, notes) VALUES(?, ?, ?, "From GMNS")"""
    conn.executemany(sql, data)
    conn.commit()
