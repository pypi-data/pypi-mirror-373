-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ For non-signalized intersections, this table lists what type of stop sign is posted
--@ in each approximation
--@

create TABLE IF NOT EXISTS Sign(
    sign_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,  --@ sign identifier
    link        INTEGER NOT NULL,                            --@ bidirectional link in which the sign is in
    dir         INTEGER NOT NULL,                            --@ direction (0 for AB, 1 for BA) in which the sign is in
    nodes       INTEGER NOT NULL DEFAULT -1,                 --@ incident node of the sign (Set by POLARIS)
    sign        TEXT    NOT NULL DEFAULT '',                 --@ sign type (ALL_STOP/STOP)

    CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED -- check
);

CREATE INDEX IF NOT EXISTS "Sign_node_idx" ON "Sign" ("nodes");
CREATE INDEX IF NOT EXISTS "Sign_link_idx" ON "Sign" ("link");

-- This guarantees that there will be only one signal per intersection
CREATE UNIQUE INDEX IF NOT EXISTS "Sign_uniqueness" ON "Sign" (nodes, link, dir);