# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import (
    add_column_unless_exists,
    has_column,
)


def migrate(conn):
    if has_column(conn, "Household", "num_groceries") and has_column(conn, "Household", "num_meals"):
        return
    add_column_unless_exists(conn, "Household", "num_groceries", "INTEGER", "DEFAULT 0")
    add_column_unless_exists(conn, "Household", "num_meals", "INTEGER", "DEFAULT 0")
