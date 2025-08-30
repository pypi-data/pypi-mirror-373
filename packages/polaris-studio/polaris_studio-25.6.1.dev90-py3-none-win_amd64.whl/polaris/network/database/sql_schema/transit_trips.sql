-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Transit_Trips table holds the complete list of all transit services
--@ operating, for which one can override the information on capacity
--@ coming from route/pattern. There is also information on whether the
--@ vehicle is articulated or if it has multiple cars (applicable to rail), but
--@ both of these fields default to 0 in case of regular bus services.
--@
--@ The transit trip ID can be traced back to the pattern, route and agency
--@ directly through the encoding of their trip_id, as explained in the
--@ documentation for the Transit_Agencies table.
--@

CREATE TABLE IF NOT EXISTS Transit_Trips(
    trip_id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,  --@ ID of the individual trip in the format AARRRRPPPPTTTT (Agency, Route, Pattern, Trip)
    trip            TEXT,                 --@ Trip identifier as shown in the GTFS feed
    dir             INTEGER NOT NULL,     --@ Direction of the trip
    pattern_id      BIGINT  NOT NULL,     --@ ID of the pattern this trip refers to
    seated_capacity INTEGER DEFAULT NULL, --@ Seated capacity of the vehicles operating this trip. Overrides the information on the transit_patterns table
    design_capacity INTEGER DEFAULT NULL, --@ Design capacity of the vehicles operating this trip. Overrides the information on the transit_patterns table
    total_capacity  INTEGER DEFAULT NULL, --@ Total capacity of the vehicles operating this trip, actually used in POLARIS as opposed to design_capacity. Overrides the information on the transit_patterns table
    is_artic        INTEGER DEFAULT 0,   -- @ Whether the vehicle is articulated or not. 1 for articulated, 0 for non-articulated. Used to calculate bus capacities, not directly used in POLARIS
    number_of_cars  INTEGER DEFAULT 0,    --@ Number of train cars operating this trip. 0 for regular bus services. Used to calculate the train capacities, not directly used in POLARIS

    FOREIGN KEY(pattern_id) REFERENCES Transit_Patterns(pattern_id) deferrable initially deferred
);