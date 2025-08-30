-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Transit_Patterns table exists because most routes have the same sequence
--@ of stops for many of its trips during the day, so it would be redundant to
--@ store the same list of stop sequence for trips with identical ones.
--@
--@ As an intermediary table between routes and trips, it is linked to both of
--@ those tables and can also have distinct capacities that override those from
--@ the routes tables whenever inserted in this table.
--@
--@ The transit pattern ID can be traced back to the route and agency directly
--@ through the encoding of their pattern_id, as explained in the documentation
--@ for the Transit_Agencies table.

--@ Due to the difficulty of map-matching GTFS feeds, it is conceivable that the
--@ route shape found during the matching problem will not be perfectly correct,
--@ so verifying the geometry of patterns is recommended.
--@

CREATE TABLE IF NOT EXISTS Transit_Patterns(
    pattern_id       INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT, --@ ID of the pattern in the format AARRRRPPPP0000 (Agency, Route, Pattern)
    pattern          TEXT     NOT NULL,     --@ Hash of the pattern. No longer relevant other than for debugging
    route_id         BIGINT   NOT NULL,     --@ ID of the route this pattern refers to
    matching_quality NUMERIC,               --@ Quality of the map-matching of the pattern to the network, if executed
    seated_capacity  INTEGER  DEFAULT NULL, --@ Seated capacity of the vehicles operating this pattern. Overrides the information on the transit_routes table
    design_capacity  INTEGER  DEFAULT NULL, --@ Design capacity of the vehicles operating this pattern. Overrides the information on the transit_routes table
    total_capacity   INTEGER  DEFAULT NULL, --@ Total capacity of the vehicles operating this pattern, actually used in POLARIS as opposed to design_capacity. Overrides the information on the transit_routes table

    FOREIGN KEY(route_id) REFERENCES Transit_Routes(route_id) deferrable initially deferred
);

select AddGeometryColumn( 'Transit_Patterns', 'geo', SRID_PARAMETER, 'LINESTRING', 'XY');

select CreateSpatialIndex( 'Transit_Patterns' , 'geo' );

