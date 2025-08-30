-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Links table holds all the links available in the road network
--@ regardless of the modes allowed on it.
--@
--@ All information on the fields node_a and node_b correspond to a entries in
--@ the node field in the node table. They are automatically managed with
--@ triggers as the user edits the network, but they are not protected by manual
--@ editing, which would break the network if it were to happen.
--@
--@ The toll_counterpart field is used to match tolled links (usually lanes)
--@ to non-tolled counterparts so that speed or density characteristics of
--@ these non-tolled links can be used to inform toll price. This is especially used
--@ in the context of managed lanes.
--@
--@ The fields **length**, **bearing_a**, **bearing_b**, **node_a** and
--@ **node_b** are automatically
--@ updated by triggers based in the links' geometries and node positions.
--@
--@
--@ The field grade has been manually computed based on the Z field for nodes
--@ and it is measured in radians from node_a to node_b. The spatialite formula
--@ for it is:
--@ Atan2("length", (Select z from node where node=node_a)-(Select z from node where node=node_b))
--@
--@ The table is indexed on **link** (its primary key), **node_a** and **node_b**.

CREATE TABLE IF NOT EXISTS Link(
 link              INTEGER UNIQUE  NOT NULL PRIMARY KEY, --@ Unique identifier of the bidirectional link
 name            TEXT                     DEFAULT '',  --@ Optional name for the segment "5th Avenue"
 node_a            INTEGER         NOT NULL DEFAULT 0,   --@ The node identifier of the "A" node that this link connects to.
 node_b            INTEGER         NOT NULL DEFAULT 0,   --@ The node identifier of the "B" node that this link connects to
 "length"          REAL                     DEFAULT 0,   --@ link length (in meters) - set by POLARIS
 setback_a         REAL                     DEFAULT 0,
 setback_b         REAL                     DEFAULT 0,
 bearing_a         INTEGER         NOT NULL DEFAULT 0,
 bearing_b         INTEGER         NOT NULL DEFAULT 0,
 "type"            TEXT            NOT NULL DEFAULT 'OTHER', --@ Road type of the link default is OTHER. Refer to Link_Type for a complete list
 area_type         INTEGER         NOT NULL DEFAULT 100,
 use               TEXT            NOT NULL DEFAULT 'ANY', --@ Not currently used by POLARIS
 grade             REAL                     DEFAULT 0,     --@ Not currently used by POLARIS
 lanes_ab          INTEGER         NOT NULL DEFAULT 0,     --@ number of lanes of the unidirectional link from node a to node b
 fspd_ab           REAL                     DEFAULT 0,     --@ free flow speed (in m/s) of the unidirectional link from node a to node b
 cap_ab            INTEGER         NOT NULL DEFAULT 0,     --@ capacity (in veh/hour) of the link from node a to node b (used only if higher than default for the scenario),
 lanes_ba          INTEGER         NOT NULL DEFAULT 0,     --@ number of lanes of the unidirectional link from node b to node a
 fspd_ba           REAL                     DEFAULT 0,     --@ free flow speed (in m/s) of the unidirectional link from node b to node a
 cap_ba            INTEGER         NOT NULL DEFAULT 0,     --@ capacity (in veh/hour) of the link from node a to node b (used only if higher than default for the scenario)
 toll_counterpart  INTEGER,                                --@ the link modeling a HOT/HOV lane that  runs in parallel with the link if existent

 CONSTRAINT "type_fk" FOREIGN KEY("type") REFERENCES "Link_Type"("link_type") DEFERRABLE INITIALLY DEFERRED,
 CONSTRAINT "area_type_fk" FOREIGN KEY("area_type") REFERENCES "Area_Type"("area_type") DEFERRABLE INITIALLY DEFERRED,
 CONSTRAINT "node_a_fk" FOREIGN KEY("node_a") REFERENCES "Node"("node") DEFERRABLE INITIALLY DEFERRED,
 CONSTRAINT "node_b_fk" FOREIGN KEY("node_b") REFERENCES "Node"("node") DEFERRABLE INITIALLY DEFERRED
 CHECK(cap_ab>=0)
 CHECK(cap_ba>=0)
 CHECK(lanes_ab>=0)
 CHECK(lanes_ba>=0)
);

SELECT AddGeometryColumn( 'Link', 'geo', SRID_PARAMETER, 'LINESTRING', 'XY', 1);
SELECT CreateSpatialIndex( 'Link' , 'geo' );

create INDEX IF NOT EXISTS link_node_a_idx ON link (node_a);
create INDEX IF NOT EXISTS link_link ON link (link);
create INDEX IF NOT EXISTS link_node_b_idx ON link (node_b);

-- These indices help in performance with check queries
create INDEX IF NOT EXISTS link_lanes_ab_idx ON link (lanes_ab);
create INDEX IF NOT EXISTS link_lanes_ba_idx ON link (lanes_ba);
