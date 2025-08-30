-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The list of pockets in the model is contained within this table, and
--@ identifies the link and direction where the pocket is located as well as its
--@ type, which is one of "RIGHT_TURN", "LEFT_TURN", "RIGHT_MERGE" or
--@ "LEFT_MERGE". The lane from which the pocket starts from, as well as its
--@ length are also part of the table.
--@
--@ Only pockets used in the connections table are included in this table.

CREATE TABLE IF NOT EXISTS Pocket(
    pocket    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    link      INTEGER,                     --@ bidirectional link containing the pocket
    dir       INTEGER NOT NULL DEFAULT 0,  --@ direction (0 for AB or 1 for BA) of the link
    node      INTEGER          DEFAULT 0,  --@ direction (0 for AB or 1 for BA) of the link
    "type"    TEXT    NOT NULL DEFAULT '', --@ type (LEFT_TURN, RIGHT_TURN)
    lanes     INTEGER NOT NULL DEFAULT 0,  --@ number of pocket lanes
    length    REAL             DEFAULT 0,  --@ length (in meters) of the pocket
    offset    REAL             DEFAULT 0,  --@ Not used by POLARIS
    
    CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED -- check
);

CREATE UNIQUE INDEX IF NOT EXISTS Pocket_unique ON Pocket (link, "dir", "type");