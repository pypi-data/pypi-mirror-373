-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Each unique signal *signal* is associated to a unique *node* in the network and has associated to it a number
--@ of different phasing schemes *times* for different times of the day, as described on **Signal_Nested_Records**.
--@
--@ Each signal is also a part of a *group* of signals (NEED DESCRIPTION OF PURPOSE HERE).
--@
--@ For the time being, the field *type* is always equal to "TIMED" and the *offset* is always 0.
--@
--@ An index on *nodes* enforces the  existence of a single signal per intersection

create TABLE IF NOT EXISTS Signal(
    signal   INTEGER NOT NULL PRIMARY KEY, --@ signal identifier
    "group"  INTEGER NOT NULL DEFAULT 0,   --@ not used by POLARIS
    times    INTEGER,                      --@ number of timing records for this signal
    nodes    INTEGER NOT NULL DEFAULT -1,  --@ actual node (Node table) that the signal infomation refers to
    "type"   TEXT    NOT NULL DEFAULT '',  --@ type (TIMED, ACTUATED). Generally TIMED is used
    offset   INTEGER NOT NULL DEFAULT 0,   --@ not used by POLARIS
    osm_id   INTEGER,                      --@ the node in open street maps of the traffic signal

    CONSTRAINT "nodes_fk" FOREIGN KEY("nodes") REFERENCES "Node"("node") DEFERRABLE INITIALLY DEFERRED
);

CREATE UNIQUE INDEX IF NOT EXISTS "Signal_signal_i" ON "Signal" ("signal");

-- This guarantees that there will be only one signal per intersection
CREATE UNIQUE INDEX IF NOT EXISTS "Signal_node_i" ON "Signal" ("nodes");