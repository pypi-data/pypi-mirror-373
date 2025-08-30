# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import has_table
from polaris.utils.database.migration_utils import move_table_to_other_db


def migrate(conn):
    if not has_table(conn, "County_Skims"):
        return

    move_table_to_other_db(conn, "County_Skims", "Supply", "Freight")
