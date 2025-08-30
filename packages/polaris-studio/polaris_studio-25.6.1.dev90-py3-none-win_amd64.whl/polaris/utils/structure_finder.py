# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from sqlite3 import Connection

from polaris.utils.database.spatialite_utils import is_spatialite


def find_table_fields(conn: Connection, table_name: str):
    from polaris.network.utils.geotypes import geotypes, spatialite_types

    structure = conn.execute(f"pragma table_info({table_name})").fetchall()
    fields = [x[1].lower() for x in structure]
    geotype = geo_field = None
    for x in structure:
        if x[2].upper() in geotypes:
            geo_field = x[1]
            geotype = x[2]
            break

    if geo_field is None and is_spatialite(conn):
        sql = f'select f_geometry_column, geometry_type from geometry_columns where f_table_name="{table_name.lower()}"'
        dt = conn.execute(sql).fetchone()
        if dt:
            geo_field = dt[0]
            geotype = spatialite_types[dt[1]]

    if geo_field is not None:
        fields = [x for x in fields if x != geo_field.lower()]

    return fields, geotype, geo_field


def find_table_index(conn: Connection, table_name: str):
    structure = conn.execute(f"pragma table_info({table_name})").fetchall()
    for x in structure:
        if x[5] == 1:
            return x[1]
    return None
