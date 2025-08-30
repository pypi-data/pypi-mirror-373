-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Transit fare zones, when applicable, are listed in this table.
--@
--@ No geometry is provided, but the information of transit zone is also
--@ available on stops whenever fares are zone based for the agency in question.
--@

CREATE TABLE IF NOT EXISTS Transit_Zones (
    transit_zone_id INTEGER NOT NULL PRIMARY KEY, --@ transit zone ID in the format AA0000000 (Agency)
    transit_zone    TEXT    NOT NULL,             --@ transit zone ID as seen in the GTFS
    agency_id       INTEGER NOT NULL,             --@ ID of the agency serving the route

    FOREIGN KEY(agency_id) REFERENCES Transit_Agencies(agency_id) deferrable initially deferred
);
