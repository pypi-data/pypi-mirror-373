# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.network.create.triggers import recreate_network_triggers
from polaris.utils.database.db_utils import has_table
from polaris.utils.database.standard_database import StandardDatabase, DatabaseType


def migrate(conn):
    conn.execute("SELECT CreateMissingSystemTables(1);")
    conn.commit()

    conn.execute("DROP TABLE if exists Editing_Table;")
    db = StandardDatabase.for_type(DatabaseType.Supply)
    if not has_table(conn, "Geo_Consistency_Controller"):
        db.add_table(conn, "Geo_Consistency_Controller", None, add_defaults=False)

    to_del = [
        "polaris_location_links_on_delete_record",
        "polaris_phasing_on_table_change",
    ]

    for trigger in to_del:
        conn.execute(f"DROP TRIGGER IF EXISTS {trigger}")
    recreate_network_triggers(conn)
