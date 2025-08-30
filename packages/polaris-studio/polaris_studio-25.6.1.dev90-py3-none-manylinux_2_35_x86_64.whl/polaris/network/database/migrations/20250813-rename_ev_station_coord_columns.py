# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import drop_column_if_exists, add_column
from polaris.network.create.triggers import recreate_network_triggers
from polaris.utils.database.db_utils import drop_trigger


def migrate(conn):
    recreate_network_triggers(conn)
    drop_trigger(conn, "polaris_ev_charging_stations_on_longitude_change")
    drop_trigger(conn, "polaris_ev_charging_stations_on_latitude_change")

    # Getting rid of the Longitude column
    # Drop all the possible lat/lon/x/y cols that might exist
    for col in ["Longitude", "Latitude", "X", "Y"]:
        drop_column_if_exists(conn, "EV_Charging_Stations", col)

    # Recreate X/Y cols in the correct order
    add_column(conn, "EV_Charging_Stations", "X", "REAL", "DEFAULT 0.0")
    add_column(conn, "EV_Charging_Stations", "Y", "REAL", "DEFAULT 0.0")

    # Updating X and Y wth the correct values
    conn.execute("update EV_Charging_Stations set Y = round(ST_Y(geo), 8),  X = round(ST_X(geo), 8)")
