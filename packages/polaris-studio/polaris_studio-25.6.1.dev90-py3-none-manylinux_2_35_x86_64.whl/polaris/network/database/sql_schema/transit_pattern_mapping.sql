-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Information pertaining to GTFS map-matching is held on this table if the
--@ feed has been map-matched during the import process. This map-matching is
--@ required for running transit in traffic, but it is not required by the
--@ transit assignment per se.

CREATE TABLE IF NOT EXISTS Transit_Pattern_Mapping(
    pattern_id BIGINT  NOT NULL, --@ ID of the transit pattern this mapping applies to
    "index"    INTEGER NOT NULL, --@ Index of the link in the pattern
    link       INTEGER NOT NULL, --@ ID of the link in the network
    dir        INTEGER NOT NULL, --@ Direction of the link in network
    stop_id    INTEGER,          --@ ID of the transit stop that projects onto the given roadway link
    offset     REAL,             --@ Distance from the start of the link to the stop in meters

    PRIMARY KEY(pattern_id,"index"),
    FOREIGN KEY(pattern_id) REFERENCES Transit_Patterns(pattern_id) deferrable initially deferred,
    FOREIGN KEY(stop_id) REFERENCES Transit_Stops(stop_id) deferrable initially deferred,
    FOREIGN KEY(link) REFERENCES Link(link) deferrable initially deferred -- check
);

CREATE INDEX IF NOT EXISTS transit_pattern_mapping_stop_id ON Transit_Pattern_Mapping (stop_id);

SELECT AddGeometryColumn( 'Transit_Pattern_Mapping', 'geo', SRID_PARAMETER, 'LINESTRING', 'XY');

SELECT CreateSpatialIndex( 'Transit_Pattern_Mapping' , 'geo' );
