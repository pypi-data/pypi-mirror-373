-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table includes information on the fields of the network that happen to
--@ diverge from their base value (contained in the link table) for any
--@ arbitrary period. This feature has not been implemented in POLARIS

CREATE TABLE IF NOT EXISTS Link_Overrides(
    link_change_id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ override identifier
    link            INTEGER,                                    --@ bi-directional link that it refers to
    field           TEXT    NOT NULL DEFAULT '',                --@ direction (0 for A to B, 1 for B to a)
    data_value      TEXT    NOT NULL,                           --@ which value to be set for the period
    from_time       INTEGER NOT NULL DEFAULT 0,                 --@ initial time (in seconds from midnight) in which the override applies
    notes           TEXT,                                       --@ any note (not read/used by POLARIS)

    CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);

create INDEX IF NOT EXISTS "idx_lnk_over_link" ON "link_overrides" ("link");