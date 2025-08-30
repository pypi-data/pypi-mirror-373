# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging

from polaris.runs.polaris_inputs import PolarisInputs
from polaris.utils.database.db_utils import add_column_unless_exists, commit_and_close, has_column, run_sql
from polaris.utils.database.standard_database import DatabaseType, StandardDatabase


def migrate(conn):
    if has_column(conn, "Household", "Has_Residential_Charging"):
        return

    # Step 1: Add the column in its new location
    add_column_unless_exists(conn, "Household", "Has_Residential_Charging", "INTEGER", "DEFAULT 0")

    # Step 2: Populate that column with data
    hh_count = conn.execute("select count(*) from Household;").fetchone()[0]
    if hh_count > 0:
        veh_count = conn.execute("select count(*) from Vehicle WHERE has_residential_charging > 0;").fetchone()[0]
        # If the database has vehicles - we can check them to see if they have res_charging true/false
        if veh_count > 0:
            sql = """
                UPDATE Household
                SET has_residential_charging = 1
                WHERE household IN (
                    SELECT hhold FROM Vehicle where has_residential_charging > 0
                );
            """
            conn.execute(sql)
        else:
            logging.warning("Your demand database has population but no vehicles with has_res_charging attribute set.")
            logging.warning("This means We can't infer which households should have the attribute set")
            logging.warning(
                "You can run the `set_has_res_charging` method to simulate it from the penetration rates "
                "in the supply file, or you can re-synthesize your population"
            )

    # Step 3: Drop the old column (either its important info was migrated to HH, or it was full of zeros)
    if has_column(conn, "Vehicle", "Has_Residential_Charging"):
        db = StandardDatabase.for_type(DatabaseType.Supply)
        db.drop_column(conn, "Vehicle", "Has_Residential_Charging")


def set_has_res_charging(files: PolarisInputs):
    # Do a random draw based on the penetration rate defined for the hh location
    # Note on a recent Austin demand.sqlite this method gives: {0:  78785, 1: 216299} (makes sense most zones have 78% penetration)
    # whereas querying the vehicles gave:                      {0: 265984, 1:  29100}
    sql = """
        UPDATE Household
        SET has_residential_charging = 1
        WHERE household IN (
            SELECT household
            FROM Household h
            JOIN supply.Location l ON h.location = l.location
            WHERE (RANDOM() + 9223372036854775808) / 18446744073709551616 < l.res_charging
        );
    """
    with commit_and_close(files.demand_db) as conn:
        run_sql(sql, conn, attach={"supply": files.supply_db})
