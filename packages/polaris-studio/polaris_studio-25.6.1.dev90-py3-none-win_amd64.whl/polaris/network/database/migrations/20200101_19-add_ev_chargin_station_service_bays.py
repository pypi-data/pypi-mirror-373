# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

from polaris.utils.database.db_utils import has_table, run_sql_file
import polaris.network.database as db


def migrate(conn):
    create_sql = Path(db.__file__).parent / "sql_schema" / "ev_charging_station_service_bays.sql"
    if not has_table(conn, "EV_Charging_Station_Service_Bays"):
        run_sql_file(create_sql, conn)
        if has_table(conn, "EV_Charging_Stations"):
            conn.execute(
                """
                INSERT INTO EV_Charging_Station_Service_Bays SELECT ID, 1 FROM EV_Charging_Stations;
            """
            )
