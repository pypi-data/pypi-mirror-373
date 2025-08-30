# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.network.create.triggers import recreate_network_triggers
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import has_table
from polaris.utils.database.standard_database import DatabaseType, StandardDatabase
from polaris.utils.database.db_utils import add_column_unless_exists


def migrate(conn):
    db = StandardDatabase.for_type(DatabaseType.Supply)
    if not has_table(conn, "Road_Connectors"):
        srid = get_srid(conn=conn)
        db.add_table(conn, "Road_Connectors", srid, add_defaults=False)
    else:
        add_column_unless_exists(conn, "Road_Connectors", "type", "TEXT", "NOT NULL DEFAULT 'LOCAL'")
        add_column_unless_exists(conn, "Road_Connectors", "bearing_a", "INTEGER", "NOT NULL DEFAULT 0")
        add_column_unless_exists(conn, "Road_Connectors", "bearing_b", "INTEGER", "NOT NULL DEFAULT 0")

    conn.commit()
    recreate_network_triggers(conn)
