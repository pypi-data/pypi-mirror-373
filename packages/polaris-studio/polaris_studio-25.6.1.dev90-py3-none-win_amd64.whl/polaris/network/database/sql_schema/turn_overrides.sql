-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Turn_Overrides table holds information on allowed turn/connection
--@ overrides to be used
--@
--@ Overriding the logic that creates the Connections table is done using
--@ this table in the following way:
--@
--@ A penalty of -1 means that this turn is prohibited
--@ A non-negative penalty means that this turn is allowed
--@
--@ The table is indexed on **node**


CREATE TABLE IF NOT EXISTS Turn_Overrides(
    turn_pen  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ ID of the override
    link      INTEGER NOT NULL,            --@ Movement coming from this link
    dir       INTEGER NOT NULL,            --@ link direction the movement is coming from
    to_link   INTEGER NOT NULL,            --@ Movement going to this link
    to_dir    INTEGER NOT NULL,            --@ link direction the movement is going to
    node      INTEGER NOT NULL,            --@ Node where the turn is happening
    penalty   INTEGER NOT NULL DEFAULT -1, --@ Penalty for the turn. -1 means the turn is blocked
    notes     TEXT,                        --@ User notes, generally why this override was instituted

    CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED, -- check
    CONSTRAINT "to_link_fk" FOREIGN KEY("to_link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED, -- check
    CONSTRAINT "to_node_fk" FOREIGN KEY("node") REFERENCES "Node"("node") DEFERRABLE INITIALLY DEFERRED
);

create INDEX IF NOT EXISTS turns_nod_idx ON Turn_Overrides (node);
CREATE UNIQUE INDEX IF NOT EXISTS turns_link_pair_idx ON Turn_Overrides (link, to_link, node);
