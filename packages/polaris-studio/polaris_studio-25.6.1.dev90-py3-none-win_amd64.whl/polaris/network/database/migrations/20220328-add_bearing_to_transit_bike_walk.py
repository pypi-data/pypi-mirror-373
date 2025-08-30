# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import add_column_unless_exists


def migrate(conn):
    add_column_unless_exists(conn, "Transit_Bike", "bearing_a", "INTEGER", "NOT NULL DEFAULT 0")
    add_column_unless_exists(conn, "Transit_Bike", "bearing_b", "INTEGER", "NOT NULL DEFAULT 0")
    add_column_unless_exists(conn, "Transit_Walk", "bearing_a", "INTEGER", "NOT NULL DEFAULT 0")
    add_column_unless_exists(conn, "Transit_Walk", "bearing_b", "INTEGER", "NOT NULL DEFAULT 0")
