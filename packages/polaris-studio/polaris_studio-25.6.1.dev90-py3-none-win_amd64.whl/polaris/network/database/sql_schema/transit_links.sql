-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table includes the hyper links connecting all pairs of consecutive
--@ stops for every transit pattern in the model.
--@

CREATE TABLE IF NOT EXISTS Transit_Links(
    transit_link  INTEGER           PRIMARY KEY, --@ Link ID of the unidirectional transit service link
    pattern_id    BIGINT  NOT NULL, --@ ID of the pattern in the format AARRRRPPPP0000 (Agency, Route, Pattern). For every from_node, to_node, pattern_id tuple, we generate a unique transit link
    from_node     INTEGER NOT NULL, --@ starting node for the link, the node being a transit stop/station from the GTFS
    to_node       INTEGER NOT NULL, --@ ending node for the link, the node being a transit stop/station from the GTFS
    length        REAL    NOT NULL, --@ length of the link in meters
    "type"        INTEGER NOT NULL, --@ indicates the type of transit mode served at this link, see transit_modes table or GTFS reference for definitions

    FOREIGN KEY(to_node) REFERENCES Transit_Stops(stop_id) deferrable initially deferred,
    FOREIGN KEY(from_node) REFERENCES Transit_Stops(stop_id) deferrable initially deferred,
    FOREIGN KEY(pattern_id) REFERENCES Transit_Patterns(pattern_id) deferrable initially deferred
);

CREATE INDEX IF NOT EXISTS transit_links_from_node ON Transit_Links (from_node);
CREATE INDEX IF NOT EXISTS transit_links_to_node ON Transit_Links (to_node);
CREATE UNIQUE INDEX IF NOT EXISTS transit_links_unique_idx ON Transit_Links (pattern_id, from_node, to_node);

SELECT AddGeometryColumn( 'Transit_Links', 'geo', SRID_PARAMETER, 'LINESTRING', 'XY');
SELECT CreateSpatialIndex( 'Transit_Links' , 'geo' );
