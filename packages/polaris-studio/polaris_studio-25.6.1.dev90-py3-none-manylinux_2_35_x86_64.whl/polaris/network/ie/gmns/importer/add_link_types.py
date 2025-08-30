# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from os import PathLike

import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess


def add_link_types(links: pd.DataFrame, conn: sqlite3.Connection, path_to_file: PathLike):
    # Thorough documentation of the assumptions used in this code is provided
    # with the package documentation
    clt = DataTableAccess(path_to_file).get("link_type", conn=conn)

    link_types = links["type"].unique()
    adds = [ltype for ltype in link_types if ltype not in clt.link_type.values]
    if not adds:
        return

    data = []
    for ltype in adds:
        uses = "|".join(list(links[links["type"] == ltype]["use"].unique()))
        data.append([ltype, 10, uses, 50, 1, "From GMNS"])

    sql = """INSERT INTO Link_Type(link_type, "rank", use_codes, turn_pocket_length, turn_pockets, notes)
                         VALUES(?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, data)
    conn.commit()
