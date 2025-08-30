# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3

from polaris.network.constants import AGENCY_MULTIPLIER
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import list_tables_in_db


def create_raw_shapes(agency_id: int, select_patterns, conn: sqlite3.Connection):
    logging.info(f"Creating transit raw shapes for agency ID: {agency_id}")

    srid = get_srid(conn=conn)

    table_list = list_tables_in_db(conn)
    if "transit_raw_shapes" not in table_list:
        conn.execute("CREATE TABLE IF NOT EXISTS TRANSIT_RAW_SHAPES (pattern_id	TEXT, route_id TEXT);")
        conn.execute(f'SELECT AddGeometryColumn( "TRANSIT_RAW_SHAPES", "geo", {srid}, "LINESTRING", "XY");')
        conn.execute('SELECT CreateSpatialIndex("Link" , "geo");')
    else:
        bottom = agency_id * AGENCY_MULTIPLIER
        top = bottom + AGENCY_MULTIPLIER
        conn.execute("Delete from TRANSIT_RAW_SHAPES where pattern_id>=? and pattern_id<?", [bottom, top])
    conn.commit()
    sql = "INSERT into Transit_raw_shapes(pattern_id, route_id, geo) VALUES(?,?, GeomFromWKB(?, ?));"
    for pat in select_patterns.values():
        if pat.raw_shape:
            conn.execute(sql, [pat.pattern_id, pat.route_id, pat.raw_shape.wkb, srid])
        else:
            conn.execute(sql, [pat.pattern_id, pat.route_id, pat._stop_based_shape.wkb, srid])
    conn.commit()
    logging.info("   Finished creating raw shapes")
