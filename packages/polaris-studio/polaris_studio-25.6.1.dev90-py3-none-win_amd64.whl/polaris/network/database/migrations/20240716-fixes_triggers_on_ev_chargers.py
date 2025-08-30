# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.network.create.triggers import recreate_network_triggers
from polaris.utils.database.db_utils import has_column


def migrate(conn):
    recreate_network_triggers(conn)
    if has_column(conn, "EV_Charging_Stations", "Latitude"):
        conn.execute("update EV_Charging_Stations set Latitude = round(ST_Y(geo), 8),  Longitude = round(ST_X(geo), 8)")
    elif has_column(conn, "EV_Charging_Stations", "X"):
        conn.execute("update EV_Charging_Stations set Y = round(ST_Y(geo), 8),  X = round(ST_X(geo), 8)")
