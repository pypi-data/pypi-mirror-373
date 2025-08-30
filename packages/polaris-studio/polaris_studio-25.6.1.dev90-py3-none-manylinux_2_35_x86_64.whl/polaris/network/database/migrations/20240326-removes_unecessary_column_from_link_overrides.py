# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import pandas as pd


def migrate(conn):
    df = pd.read_sql("SELECT * FROM Link_Overrides", conn)

    sqls = [
        "DROP TABLE IF EXISTS Link_Overrides",
        """CREATE TABLE IF NOT EXISTS Link_Overrides (
                link_change_id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                link            INTEGER,
                field           TEXT    NOT NULL DEFAULT '',
                data_value      TEXT    NOT NULL,
                from_time       INTEGER NOT NULL DEFAULT 0,
                notes           TEXT,

                CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED
            );""",
        """DROP INDEX IF EXISTS "idx_lnk_over_link";""",
        """create INDEX IF NOT EXISTS "idx_lnk_over_link" ON "link_overrides" ("link");""",
    ]

    for sql in sqls:
        conn.execute(sql)

    if df.empty:
        return

    df = df.drop(columns=["to_time"], errors="ignore")
    df = df.rename(columns={"override": "link_change_id"}, errors="ignore")
    df.to_sql("Link_Overrides", conn, if_exists="append", index=False)
