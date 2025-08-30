# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike

from polaris.utils.database.data_table_access import DataTableAccess


def add_land_uses(locations, conn, path_to_file: PathLike):
    # Thorough documentation of the assumptions used in this code is provided
    # with the package documentation
    clu = DataTableAccess(path_to_file).get("Land_Use", conn=conn)

    land_uses = locations["land_use"].unique()
    adds = [luse for luse in land_uses if luse not in clu.land_use.values]
    if not adds:
        return

    data = [[luse, 1, 1, 1, 1, "From GMNS"] for luse in adds]
    sql = """INSERT INTO Land_Use(land_use, is_home, is_work, is_school, is_discretionary, notes)
                         VALUES(?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, data)
    conn.commit()
