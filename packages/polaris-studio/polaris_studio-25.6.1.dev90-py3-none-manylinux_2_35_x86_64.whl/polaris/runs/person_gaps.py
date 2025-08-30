# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import commit_and_close


drop_sql = "DROP Table IF EXISTS Person_Gaps;"
create_sql = """
    CREATE TABLE person_gaps
    (
        "person"  INTEGER NULL,
        "avg_gap" REAL NULL DEFAULT 0,
        PRIMARY KEY("person"),
        CONSTRAINT "person_fk" FOREIGN KEY ("person") REFERENCES "person" ("person") deferrable initially deferred
    ); 
"""
populate_sql = """
    INSERT INTO person_gaps
    SELECT person, SUM(CASE
                    WHEN (has_artificial_trip = 0 OR has_artificial_trip = 3 OR has_artificial_trip = 4)
                        THEN Max(end - start - routed_travel_time, 0)
                    WHEN has_artificial_trip = 2 THEN 2 * routed_travel_time
                    END) / SUM(routed_travel_time) AS avg_gap
    FROM "trip"
    WHERE  MODE IN (0,9)
        AND type = 11
        AND has_artificial_trip <> 1
        AND end > start
        AND routed_travel_time > 0
    GROUP BY person; 
"""


def generate_person_gaps(demand_db):
    with commit_and_close(demand_db) as conn:
        conn.execute(drop_sql)
        conn.execute(create_sql)
        conn.execute(populate_sql)
