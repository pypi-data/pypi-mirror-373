# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.network.create.triggers import recreate_network_triggers
from polaris.utils.database.db_utils import drop_trigger, get_trigger_sql, remove_table
from polaris.utils.database.standard_database import DatabaseType, StandardDatabase


def migrate(conn):
    db = StandardDatabase.for_type(DatabaseType.Supply)
    conn.execute("pragma foreign_keys = off;")

    # There seems to be some kind of bug in two spatialite triggers which is triggered when dropping columns
    # We check if they exist and if so drop them and recreate them later
    sql_insert = get_trigger_sql(conn, "ISO_metadata_reference_row_id_value_insert")
    sql_update = get_trigger_sql(conn, "ISO_metadata_reference_row_id_value_update")
    if sql_insert is not None:
        drop_trigger(conn, "ISO_metadata_reference_row_id_value_insert")
        drop_trigger(conn, "ISO_metadata_reference_row_id_value_update")

    recreate_network_triggers(conn)

    # these triggers have been flat out deleted
    drop_trigger(conn, "network_preserves_speed_ab_direction")
    drop_trigger(conn, "network_speed_ab_only_positive_for_available_direction")
    drop_trigger(conn, "network_preserves_speed_ba_direction")
    drop_trigger(conn, "network_speed_ba_only_positive_for_available_direction")

    remove_table(conn, "detector", missing_okay=True)
    # remove_table(conn, "use_code", missing_okay=True)

    db.drop_column(conn, "Phasing", "detectors")
    location_columns = ["truck_org", "truck_des", "auto_org", "auto_des", "transit", "anchored"]
    # db.drop_columns(conn, "ev_charging_stations ", ["num_plugs", "num_plugs_dcfc", "num_plugs_l2"])
    db.drop_columns(conn, "Link", ["divided", "speed_ab", "speed_ba", "left_ab", "left_ba", "right_ab", "right_ba"])
    db.drop_columns(conn, "Location", location_columns)
    db.drop_columns(conn, "Node", ["subarea", "part"])
    db.drop_columns(conn, "Parking", ["permit", "evse"])
    db.drop_columns(conn, "Zone", ["min_x", "min_y", "max_x", "max_y"])

    conn.execute("pragma foreign_keys = on;")

    # add back the spatialite triggers (if removed)
    if sql_insert is not None:
        conn.execute(sql_insert)
        conn.execute(sql_update)
