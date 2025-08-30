-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The connections table lists the possible turns from one link into another
--@ (or itself). It specifies the lane(s) in the origin and destination links
--@ that are connected, as well as the detail of topological direction in each
--@ link that corresponds to that connection.
--@
--@ Geometry information is provided solely for visualization purposes

CREATE TABLE IF NOT EXISTS Connection(
    conn        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    link        INTEGER,                     --@ bidirectional link for the upstream link of the connection
    dir         INTEGER NOT NULL DEFAULT 0,  --@ direction (0 for ab, 1 for ba) of the upstream link of the connection
    node        INTEGER,                     --@ incident node of the connection (set by POLARIS)
    to_link     INTEGER NOT NULL,            --@ downstream bidirectinal link of the connection
    to_dir      INTEGER,                     --@ direction (1 for ab, 1 for ba) of the downstream link of the connection
    lanes       TEXT             DEFAULT '', --@ number of lanes in the upstream link that can be used for the connection (not used for all models)
    to_lanes    TEXT    NOT NULL DEFAULT '', --@ number of lanes in the downstream link that can be used for the connection (not used for all models)
    "type"        TEXT    NOT NULL DEFAULT '', --@ movement type (THRU, RIGHT, LEFT, UTURN)
    penalty     INTEGER NOT NULL DEFAULT 0,  --@ Not used by POLARIS
    speed       REAL             DEFAULT 0,  --@ Not used by POLARIS
    capacity    INTEGER NOT NULL DEFAULT 0,  --@ Not used by POLARIS
    in_high     INTEGER NOT NULL DEFAULT 0,  --@ Not used by POLARIS
    out_high    INTEGER NOT NULL DEFAULT 0,  --@ Not used by POLARIS
    approximation TEXT    NOT NULL DEFAULT '', --@ directional approximation SB (southbound), EB, NB or WB

    CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "to_link_fk" FOREIGN KEY("to_link") REFERENCES "Link"("link") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "node_fk" FOREIGN KEY("node") REFERENCES "Node"("node") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);

SELECT AddGeometryColumn( 'Connection', 'geo', SRID_PARAMETER, 'LINESTRING', 'XY');
SELECT CreateSpatialIndex( 'Connection' , 'geo' );

create INDEX IF NOT EXISTS "idx_conn_node" ON "Connection" ("node");
create INDEX IF NOT EXISTS "idx_conn_lanes" ON "Connection" ("lanes");
create INDEX IF NOT EXISTS "idx_conn_to_lanes" ON "Connection" ("to_lanes");
create INDEX IF NOT EXISTS "idx_conn_link" ON "Connection" ("link");
create INDEX IF NOT EXISTS "idx_conn_to_link" ON "Connection" ("to_link");
