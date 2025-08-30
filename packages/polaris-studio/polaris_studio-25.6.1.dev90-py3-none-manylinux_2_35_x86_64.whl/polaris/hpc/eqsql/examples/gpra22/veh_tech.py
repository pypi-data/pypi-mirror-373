# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import has_table, commit_and_close
from polaris.utils.logging_utils import function_logging


@function_logging("  Factoring up EV plugs by {factor}")
def factor_up_ev_plugs(supply_db, factor):
    with commit_and_close(supply_db) as conn:
        if not has_table(conn, "EV_Charging_Station_Plugs_orig"):
            conn.execute("CREATE TABLE EV_Charging_Station_Plugs_orig as SELECT * FROM EV_Charging_Station_Plugs;")
        conn.execute("DELETE FROM EV_Charging_Station_Plugs;")
        conn.execute(
            f"""
          INSERT INTO EV_Charging_Station_Plugs 
          SELECT station_id, plug_type, cast(round({factor} * plug_count, 0) as int) 
          FROM EV_Charging_Station_Plugs_orig;
        """
        )
