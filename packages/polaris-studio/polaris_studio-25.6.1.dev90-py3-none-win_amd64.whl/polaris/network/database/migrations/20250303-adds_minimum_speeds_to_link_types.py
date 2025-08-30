# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import has_column, add_column


def migrate(conn):
    if has_column(conn, "Link_Type", "minimum_speed"):
        return
    add_column(conn, "Link_Type", "minimum_speed", "NUMERIC", "DEFAULT 0")

    conn.execute("UPDATE Link_Type SET minimum_speed=1000")

    speeds = {
        "FREEWAY": 25,
        "EXPRESSWAY": 25,
        "PRINCIPAL": 10,
        "MAJOR": 10,
        "MINOR": 10,
        "COLLECTOR": 10,
        "LOCAL_THRU": 10,
        "LOCAL": 10,
        "FRONTAGE": 10,
        "RAMP": 20,
        "BRIDGE": 10,
        "TUNNEL": 10,
        "EXTERNAL": 25,
        "WALKWAY": 0,
        "BIKEWAY": 0,
        "BUSWAY": 10,
        "LIGHTRAIL": 0,
        "HEAVYRAIL": 0,
        "FERRY": 0,
        "OTHER": 10,
        "WALK": 0,
        "TRANSIT": 0,
    }

    for ltype, min_speed in speeds.items():
        conn.execute("UPDATE Link_Type SET minimum_speed=? WHERE link_type=?", [min_speed, ltype])
    conn.commit()
