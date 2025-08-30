# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import add_column_unless_exists


def migrate(conn):
    add_column_unless_exists(conn, "Link_Type", "speed_limit", "NUMERIC", "DEFAULT 0")

    speeds = {
        "FREEWAY": 33,
        "EXPRESSWAY": 33,
        "PRINCIPAL": 28,
        "MAJOR": 28,
        "MINOR": 28,
        "COLLECTOR": 27,
        "LOCAL_THRU": 22,
        "LOCAL": 22,
        "FRONTAGE": 28,
        "RAMP": 33,
        "BRIDGE": 33,
        "TUNNEL": 33,
        "EXTERNAL": 33,
        "WALKWAY": 10,
        "BIKEWAY": 10,
        "BUSWAY": 10,
        "LIGHTRAIL": 20,
        "HEAVYRAIL": 20,
        "FERRY": 20,
        "OTHER": 27,
        "WALK": 10,
        "TRANSIT": 10,
    }

    for ltype, max_speed in speeds.items():
        conn.execute("UPDATE Link_Type SET speed_limit=? WHERE link_type=? AND speed_limit=0", [max_speed, ltype])
    conn.commit()

    conn.execute("UPDATE Link_Type SET speed_limit=10 WHERE speed_limit=0")
