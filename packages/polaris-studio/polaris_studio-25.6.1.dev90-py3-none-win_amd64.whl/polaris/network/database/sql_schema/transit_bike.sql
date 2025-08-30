-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ For now, this table is an exact copy of the Transit_Walk table
--@

CREATE TABLE IF NOT EXISTS "Transit_Bike" (
    bike_link    INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT, --@ Bike link ID
    from_node    INTEGER  NOT NULL,           --@ starting node for the link. Can be a regular network node or a virtual node created to articulate the network
    to_node      INTEGER  NOT NULL,           --@ same as the from_node but for the end of the link
    bearing_a    INTEGER  NOT NULL DEFAULT 0, --@ Geographic bearing at the start of the link
    bearing_b    INTEGER  NOT NULL DEFAULT 0, --@ Geographic bearing at the end of the link
    "length"     REAL     NOT NULL,           --@ Length of the link in meters
    ref_link     INTEGER  NOT NULL default 0  --@ Reference to the link in the roadway network (**link** table), if any
);

SELECT AddGeometryColumn('Transit_Bike', 'geo', SRID_PARAMETER, 'LINESTRING', 'XY', 1);
SELECT CreateSpatialIndex('Transit_Bike' , 'geo');

UPDATE SQLITE_SEQUENCE SET seq = 4000000 WHERE name = 'Transit_Bike';

CREATE INDEX IF NOT EXISTS transit_bike_from_node ON Transit_Bike (from_node);
CREATE INDEX IF NOT EXISTS transit_bike_to_node ON Transit_Bike (to_node);
