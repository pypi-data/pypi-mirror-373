-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all the transit stops in the model on which at least one transit trip
--@ stops during the day. It  lists the agency it is associated to, as well as
--@ the closest network link to it
--@
--@ Additionally to transit stops, this table also holds nodes in the network
--@ associated with the active networks (walk and bike), more specifically the
--@ nodes created in the network to allow transit stops to be linked in what was
--@ previously the middle of a network link.

--@ If a node had to be moved during the GTFS map-matching (probably due to a
--@ too-sparse of a network), then the moved_by_matching field will contain the
--@ straight-line distance the stop was moved.


-- TODO: *link*, *dir*, *offset*, setback** and those for coordinates x/y/z should have the same treatment
CREATE TABLE IF NOT EXISTS Transit_Stops(
    stop_id           INTEGER PRIMARY KEY AUTOINCREMENT , --@ ID of the stop/station used by POLARIS in the format AA0000000 (Agency)
    stop              TEXT    NOT NULL ,           --@ stop ID as seen in GTFS
    agency_id         INTEGER NOT NULL,            --@ ID of the agency to which the stop belongs to
    X                 REAL    NOT NULL DEFAULT 0 , --@ x coordinate of the stop in meters
    Y                 REAL    NOT NULL DEFAULT 0 , --@ y coordinate of the stop in meters
    Z                 REAL    NOT NULL DEFAULT 0 , --@ z coordinate of the stop in meters
    name              TEXT,                        --@ name of the stop as seen in GTFS
    parent_station    TEXT,                        --@ parent station of the stop as seen in GTFS
    description       TEXT,                        --@ description of the stop as seen in GTFS
    street            TEXT,                        --@ name of the stop as seen in GTFS
    zone              INTEGER,                     --@ zone of the stop as seen in the zone table
    transit_zone_id   INTEGER,                     --@ transit zone of the stop as seen in the transit_zones table
    has_parking       INTEGER NOT NULL DEFAULT 0 , --@ indicates whether cars can park by the station for the park-and-ride and park-and-rail modes
    route_type        INTEGER NOT NULL DEFAULT -1, --@ indicates the type of transit mode served at this stop, see transit_modes table or GTFS reference for definitions
    moved_by_matching INTEGER DEFAULT 0,           --@ indicates whether the stop is relocated by the map matching process

    FOREIGN KEY(agency_id) REFERENCES "Transit_Agencies"(agency_id),
    FOREIGN KEY("zone") REFERENCES "Zone"("zone") deferrable initially deferred,
    FOREIGN KEY("transit_zone_id") REFERENCES "Transit_Zones"("transit_zone_id")
);

create INDEX IF NOT EXISTS transit_stops_stop_id ON Transit_Stops (stop_id);

select AddGeometryColumn( 'Transit_Stops', 'geo', SRID_PARAMETER, 'POINT', 'XY', 1);
select CreateSpatialIndex( 'Transit_Stops' , 'geo' );
