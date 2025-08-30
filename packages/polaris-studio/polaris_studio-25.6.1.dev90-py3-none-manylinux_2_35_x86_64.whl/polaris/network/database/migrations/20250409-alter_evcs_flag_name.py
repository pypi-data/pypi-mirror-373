# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3

import pandas as pd

from polaris.network.create.triggers import delete_triggers, create_triggers
from polaris.utils.database.db_utils import drop_trigger, get_trigger_sql
from polaris.utils.database.db_utils import has_column, drop_column, add_column_unless_exists
from polaris.utils.database.standard_database import StandardDatabase, DatabaseType


def migrate(conn: sqlite3.Connection):
    # If reading from csv - then both columns exist
    # Return only if Station_Type has completely replaced Public_Flag
    if has_column(conn, "EV_Charging_Stations", "Station_Type") and not has_column(
        conn, "EV_Charging_Stations", "Public_Flag"
    ):
        return

    delete_triggers(StandardDatabase.for_type(DatabaseType.Supply), conn)
    df = pd.read_sql("SELECT * FROM EV_Charging_Stations", conn)
    # When creating a new DB, remove column Station_Type and use values from Public_Flag
    if "Station_Type" in df:
        df = df.drop("Station_Type", axis=1)
    # Rename Public_Flag to use its data for the migrated DB
    df = df.rename(columns={"Public_Flag": "Station_Type"}, errors="ignore")
    # previous public_flag is a boolean (0 = private, 1 = public)
    # creating station_type now with enum as (public=0, private=1, freight=2)
    df.Station_Type = df.Station_Type.replace({0: 1, 1: 0, 2: 2})

    triggers = ["ISO_metadata_reference_row_id_value_update", "ISO_metadata_reference_row_id_value_insert"]

    sqls = []
    for trigger in triggers:
        sql = get_trigger_sql(conn, trigger)
        if sql:
            sqls.append(sql)
            drop_trigger(conn, trigger)

    conn.commit()
    drop_column(conn, "EV_Charging_Stations", "Public_Flag")
    add_column_unless_exists(conn, "EV_Charging_Stations", "Station_Type", "INTEGER", "DEFAULT 1")
    for sql in sqls:
        conn.execute(sql)

    data = df[["Station_Type", "ID"]].to_records(index=False)
    conn.executemany("UPDATE EV_Charging_Stations SET Station_Type = ? WHERE ID = ?", data)
    create_triggers(StandardDatabase.for_type(DatabaseType.Supply), conn)
