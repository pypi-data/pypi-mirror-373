# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import has_table


def migrate(conn):
    # This is copied from update-scripts / supply_update22-add_rsu_incidents_tables.sql
    # https://git-in.gss.anl.gov/polaris-model-contributers/update-scripts/-/blob/master/supply_update22-add_rsu_incidents_tables.sql
    if not has_table(conn, "Traffic_Incident"):
        sql = """
            CREATE TABLE "Traffic_Incident" (
                "link"	            INTEGER NOT NULL,
                "dir"	            INTEGER NOT NULL DEFAULT 0,
                "start_time"	    INTEGER NOT NULL DEFAULT 0,
                "end_time"	        INTEGER NOT NULL DEFAULT 0,
                "capacity_scale"	        	REAL    NOT NULL DEFAULT 0,
                CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED
            ); """
        conn.execute(sql)

    if not has_table(conn, "RoadSideUnit"):
        sql = """
            CREATE TABLE RoadSideUnit
            (
                "unit_id" INTEGER UNIQUE NOT NULL PRIMARY KEY,
                "link"	            INTEGER NOT NULL,
                "dir"	            INTEGER NOT NULL DEFAULT 0,
                "position" real NOT NULL DEFAULT 0,
                "power" REAL not null DEFAULT 0,
                "collected_info" TEXT,
                "Logging_interval_seconds" int not null DEFAULT 0,
                CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED
            ); """
        conn.execute(sql)
