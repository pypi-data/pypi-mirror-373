-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Transit fares can be associated to routes, in cases where routes have flat
--@ fares regardless of boarding and alighting stops. The other possible
--@ association is through the existing of fare zones, where trips are charged
--@ based on the combination of the transit zones for boarding and alighting.
--@
--@ This table includes both associations, thus records would have either the
--@ route_id or origin/destination fields as null.

create TABLE IF NOT EXISTS Transit_Fare_Rules (
    fare_id     INTEGER NOT NULL, --@ ID of the trip in the format AA000000000000 (Agency)
    route_id    BIGINT,           --@ ID of the route to which this fare applies, not currently used in POLARIS but is kept for consistency with the GTFS
    origin      INTEGER,          --@ Identifies an origin transit zone as seen in transit_zones table. For every unique origin-destination pair, create an entry.
    destination INTEGER,          --@ Identifies a destination transit zone as seen in transit_zones table. For every unique origin-destination pair, create an entry.
    "contains"  INTEGER,          --@ Identifies the zones that a rider will enter while using a given fare class, not currently used in POLARIS but is kept for consistency with the GTFS

    FOREIGN KEY(fare_id) REFERENCES Transit_Fare_Attributes(fare_id) deferrable initially deferred,
    FOREIGN KEY(route_id) REFERENCES Transit_Routes(route_id) deferrable initially deferred,
    FOREIGN KEY(destination) REFERENCES Transit_Zones(transit_zone_id) deferrable initially deferred,
    FOREIGN KEY(origin) REFERENCES Transit_Zones(transit_zone_id) deferrable initially deferred,
    FOREIGN KEY(contains) REFERENCES Transit_Zones(transit_zone_id) deferrable initially deferred
);
