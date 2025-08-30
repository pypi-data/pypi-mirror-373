# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import has_table
from polaris.utils.database.standard_database import DatabaseType, StandardDatabase


def migrate(conn):
    if not has_table(conn, "about_model"):
        StandardDatabase.for_type(DatabaseType.Demand).add_table(conn, "about_model", None, add_defaults=False)
