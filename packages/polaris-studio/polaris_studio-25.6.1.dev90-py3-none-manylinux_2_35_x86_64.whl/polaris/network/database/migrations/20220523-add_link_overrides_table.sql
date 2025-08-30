-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
CREATE TABLE IF NOT EXISTS "Link_Overrides" (
    "override"      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "link"          INTEGER,
    "field"          TEXT    NOT NULL DEFAULT '',
    "data_value"    TEXT    NOT NULL,
    "from_time"     INTEGER NOT NULL DEFAULT 0,
    "to_time"       INTEGER NOT NULL DEFAULT 86400,
    "notes"          TEXT,
    CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED
);

create INDEX IF NOT EXISTS "idx_lnk_over_link" ON "link_overrides" ("link");