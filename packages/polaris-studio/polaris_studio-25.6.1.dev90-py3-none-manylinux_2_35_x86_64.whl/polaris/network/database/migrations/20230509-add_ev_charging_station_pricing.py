# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

from polaris.utils.database.db_utils import run_sql_file


def migrate(conn):
    sql_file = Path(__file__).absolute().parent.parent / "sql_schema" / "ev_charging_station_pricing.sql"
    run_sql_file(sql_file, conn)
