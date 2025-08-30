-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The node table contains the nodes corresponding to the extremities of all
--@ links from the Link table. Each entry is the start or end point of at least
--@ one link in the Link table
--@
--@ The fields **x** and **y** are automatically updated by triggers based
--@ the nodes' geometries.
--@
--@ THe geometry field has no elevation support, but the **z** field has been
--@ manually computed through geo-processing of DEM data
--@
--@ The table is indexed on **node** (its primary key)

create TABLE IF NOT EXISTS Node(
    node           INTEGER UNIQUE NOT NULL PRIMARY KEY, --@ unique identifier of the node
    x              REAL,                                --@ X coord set by POLARIS
    y              REAL,                                --@ Y coord set by POLARIS
    z              REAL,                                --@ Z coord set by POLARIS
    control_type   TEXT,                                --@ Control type of the node (signal, all_stop, stop_sign)
    zone           INTEGER,                             --@ zone identifier of the link
    
    FOREIGN KEY("zone") REFERENCES "Zone"("zone") deferrable initially deferred
 );

select AddGeometryColumn( 'Node', 'geo', SRID_PARAMETER, 'POINT', 'XY', 1);
select CreateSpatialIndex( 'Node' , 'geo' );

create INDEX IF NOT EXISTS "NODE_NODE_I" ON "Node" ("node");
