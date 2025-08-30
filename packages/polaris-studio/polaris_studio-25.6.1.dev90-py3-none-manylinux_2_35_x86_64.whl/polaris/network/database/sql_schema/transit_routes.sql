-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The transit routes correspond to the routes table in GTFS feeds, but this
--@ table includes only those routes for which that are active services for the
--@ for which services have been imported. Descriptive information, as well as
--@ capacity is included in this table, although the latter can be overwritten
--@ if information is provided in the transit_patterns or transit_trips tables.
--@
--@ The routes can be traced back to the agency directly through the encoding of
--@ their trip_id, as explained in the documentation for the Transit_Agencies
--@ table.

CREATE TABLE IF NOT EXISTS Transit_Routes(
    route_id        INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT, --@ ID of the route in the format AARRRR00000000 (Agency, Route)
    route           TEXT     NOT NULL, --@ ID of the route as defined in the GTFS
    agency_id       INTEGER  NOT NULL, --@ ID of the agency serving the route
    shortname       TEXT,              --@ short name of the route as seen in the GTFS
    longname        TEXT,              --@ long name of the route as seen in the GTFS
    description     TEXT,              --@ description of the route as seen in the GTFS
    "type"          INTEGER  NOT NULL, --@ indicates the type of transit mode served by this route, see transit_modes table or GTFS reference for definitions
    seated_capacity INTEGER,           --@ Seated capacity of the vehicles operating this route.
    design_capacity INTEGER,           --@ Design capacity of the vehicles operating this route. 
    total_capacity  INTEGER,           --@ Total capacity of the vehicles operating this route, actually used in POLARIS as opposed to design_capacity.
    number_of_cars  INTEGER DEFAULT 0, --@ Number of train cars operating this route. 0 for regular bus services. Used to calculate the train capacities, not directly used in POLARIS

    FOREIGN KEY(agency_id) REFERENCES Transit_Agencies(agency_id) deferrable initially deferred
);


select AddGeometryColumn( 'Transit_Routes', 'geo', SRID_PARAMETER, 'MULTILINESTRING', 'XY');

select CreateSpatialIndex( 'Transit_Routes' , 'geo' );