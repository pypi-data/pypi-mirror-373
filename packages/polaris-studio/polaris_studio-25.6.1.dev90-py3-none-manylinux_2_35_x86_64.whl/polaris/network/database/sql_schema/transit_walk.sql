-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table is the junction of two different types of links:
--@    * Network links (from the links table) that can be traversed by walk
--@    * Access links connecting stops and micro-mobility docks to the network
--@
--@ This network is static and should be re-created any time there are changes
--@ in the transit data (e.g. import of a new GTFS feed), or whenever new
--@ micromobility docks are added to the supply database.
--@
--@ It important to understand that the number of links in this network is
--@ substantially larger than in the **links** table because it has links
--@ connecting each stop/dock to the physical network, as well as links
--@ connecting transit stops (and docks) stops directly to each other whenever
--@ they are very close (the distance between them is half of that between them
--@ and the physical network.
--@
--@ Physical links are also broken to allow stops to be connected by walk in the
--@ middle of links, where stops are actually located. We attempt to reduce the
--@ number of link breaks by combining access links into the same point whenever
--@ possible and without penalizing agents with substantially longer walk
--@ distances.

CREATE TABLE IF NOT EXISTS Transit_Walk(
    walk_link INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT, --@ Walk link ID
    from_node INTEGER  NOT NULL,      --@ node start for the link. Can be a regular network node or as virtual node created to articulate the network
    to_node   INTEGER  NOT NULL,      --@ same as the from_node but for the end of the link
    bearing_a INTEGER  NOT NULL DEFAULT 0, --@ Geographic bearing at the start of the link
    bearing_b INTEGER  NOT NULL DEFAULT 0, --@ Geographic bearing at the end of the link
    length    REAL     NOT NULL,           --@ Length of the link in meters
    ref_link  INTEGER  NOT NULL default 0  --@ Reference to the link in the roadway network (**link** table), if any
);

SELECT AddGeometryColumn('Transit_Walk', 'geo', SRID_PARAMETER, 'LINESTRING', 'XY', 1);

UPDATE SQLITE_SEQUENCE SET seq = 3000000 WHERE name = 'Transit_Walk';

SELECT CreateSpatialIndex('Transit_Walk' , 'geo');


CREATE INDEX IF NOT EXISTS transit_walk_from_node ON Transit_Walk (from_node);

CREATE INDEX IF NOT EXISTS transit_walk_to_node ON Transit_Walk (to_node);
