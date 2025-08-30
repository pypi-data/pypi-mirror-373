# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import has_table, add_column_unless_exists
from polaris.utils.database.standard_database import DatabaseType, StandardDatabase


def migrate(conn):
    db = StandardDatabase.for_type(DatabaseType.Supply)
    if not has_table(conn, "Electricity_Provider"):
        db.add_table(conn, "Electricity_Provider", None, add_defaults=True)

    db = StandardDatabase.for_type(DatabaseType.Supply)
    if not has_table(conn, "Electricity_Provider_Pricing"):
        db.add_table(conn, "Electricity_Provider_Pricing", None, add_defaults=True)

    db = StandardDatabase.for_type(DatabaseType.Supply)
    if not has_table(conn, "Electricity_Grid_Transmission"):
        db.add_table(conn, "Electricity_Grid_Transmission", None, add_defaults=True)

    add_column_unless_exists(conn, "Zone", "electric_grid_transmission", "INTEGER", "NOT NULL DEFAULT 1")
    add_column_unless_exists(conn, "Zone", "electricity_provider", "INTEGER", "NOT NULL DEFAULT 1")
