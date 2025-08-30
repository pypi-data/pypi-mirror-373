# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import has_table
from polaris.utils.database.standard_database import DatabaseType, StandardDatabase


def migrate(conn):
    demand_db = StandardDatabase.for_type(DatabaseType.Demand)
    if not has_table(conn, "Mode"):
        demand_db.add_table(conn, "Mode", None, add_defaults=True)
    if not has_table(conn, "Activity_Type"):
        demand_db.add_table(conn, "Activity_Type", None, add_defaults=True)
