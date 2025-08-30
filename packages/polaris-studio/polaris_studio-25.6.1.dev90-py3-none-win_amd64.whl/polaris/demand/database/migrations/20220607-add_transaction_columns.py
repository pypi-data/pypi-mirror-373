# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import add_column_unless_exists


def migrate(conn):
    # Alter TABLE Household    add  time_in_home real default 0.0;
    # Alter TABLE Person       add  time_in_job real default 0.0;
    # Alter TABLE Vehicle_Type add  operating_cost_per_mile real default 0.18;
    add_column_unless_exists(conn, "Household", "time_in_home", "REAL", "DEFAULT 0.0")
    add_column_unless_exists(conn, "Person", "time_in_job", "REAL", "DEFAULT 0.0")
    add_column_unless_exists(conn, "Vehicle_Type", "operating_cost_per_mile", "REAL", "DEFAULT 0.18")
