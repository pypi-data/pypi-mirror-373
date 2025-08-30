-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Transit_agencies table holds information on all the transit agencies
--@ for which there are transit services included in the model.
--@ information for these agencies include the GTFS feed (feed_date) and
--@ operation day (service_date) for which services were imported into the
--@ model.
--@
--@ Encoding of ids for transit agencies, routes, patterns and trips follows a
--@ strict encoding that allow one to trace back each element to its parent
--@ (Agency->Route->Pattern->Trip).
--@ This encoding follows the following pattern: AARRRPPTTT. Since this IDs
--@ are always integer, those corresponding to agencies 1 through 9 will omit
--@ the first 0 in the ID pattern shown above.
--@

create TABLE IF NOT EXISTS Transit_Agencies(
    agency_id    INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT, --@ ID of the agency. 1 is reserved for a dummy agency for walking links
    agency       TEXT    NOT NULL, --@ Name of the agency as imported
    feed_date    TEXT,             --@ Release date for the GTFS feed used
    service_date TEXT,             --@ The service date used for importing the GTFS feed
    description  TEXT              --@ User notes
);

create UNIQUE INDEX IF NOT EXISTS transit_operators_id ON Transit_Agencies (agency_id);
