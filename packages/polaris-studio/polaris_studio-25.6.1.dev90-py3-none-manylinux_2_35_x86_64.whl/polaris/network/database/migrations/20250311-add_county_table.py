# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import has_table
from polaris.utils.database.standard_database import DatabaseType, StandardDatabase


def migrate(conn):
    db = StandardDatabase.for_type(DatabaseType.Supply)
    if not has_table(conn, "counties"):
        db.add_table(conn, "counties", get_srid(conn=conn), add_defaults=False)
