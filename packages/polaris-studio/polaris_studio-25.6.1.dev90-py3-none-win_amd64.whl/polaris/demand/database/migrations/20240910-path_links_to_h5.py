# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

from polaris.utils.database.db_utils import add_column_unless_exists


def migrate(conn):
    add_column_unless_exists(conn, "Trip", "initial_energy_level", "REAL", "DEFAULT 0")
    add_column_unless_exists(conn, "Trip", "final_energy_level", "REAL", "DEFAULT 0")
