-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Road_Connectors table holds all virtual links necessary to connect the road network
--@ to other infrastructure, such as ferry services
--@
--@ To this extent, each road connector must have one extremity (from_node/to_node) set to 
--@ a node in the network, and the other extremity set to a member (node) if a different table (e.g. transit stop).

CREATE TABLE IF NOT EXISTS Road_Connectors(
 road_connector    INTEGER UNIQUE  NOT NULL PRIMARY KEY,   --@ Unique identifier of the bidirectional road connector
 from_node         INTEGER         NOT NULL DEFAULT 0,     --@ The node identifier of the "from" node that this link connects to.
 to_node           INTEGER         NOT NULL DEFAULT 0,     --@ The node identifier of the "to" node that this link connects to
 length            REAL            NOT NULL DEFAULT 0,     --@ link length (in meters) - set by POLARIS based on the link geometry
 use               TEXT            NOT NULL DEFAULT 'ANY|AUTO|WALK',  --@ If different than ANY, restricts the use of this link to the specified vehicle types
 "type"            TEXT            NOT NULL DEFAULT 'LOCAL',          --@ Default road type for auto access based on purpose
 fspd_ab           REAL                     DEFAULT 0,     --@ free flow speed (in m/s) of the unidirectional link from from_node to from_node
 fspd_ba           REAL                     DEFAULT 0,     --@ free flow speed (in m/s) of the unidirectional link from to_node to from_node
 purpose           TEXT            NOT NULL DEFAULT 0,                --@ The reason for the existence of this link (e.g. ferry_access)
 bearing_a         INTEGER         NOT NULL DEFAULT 0,                --@ Trigger-added bearing info for link from node a
 bearing_b         INTEGER         NOT NULL DEFAULT 0                 --@ Trigger-added bearing info for link from node b
);

UPDATE SQLITE_SEQUENCE SET seq = 5000000 WHERE name = 'Road_Connectors';

-- Adds geo-components to the table
SELECT AddGeometryColumn('Road_Connectors', 'geo', SRID_PARAMETER, 'LINESTRING', 'XY', 1);
SELECT CreateSpatialIndex('Road_Connectors', 'geo');

