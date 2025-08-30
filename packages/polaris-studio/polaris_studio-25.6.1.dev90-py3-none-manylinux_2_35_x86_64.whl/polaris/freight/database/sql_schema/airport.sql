-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Airport Point of Entry (POE) table contains
--@ the attributes of airports that are within the modelled city,
--@ including the airport name, the geographic information,
--@ and the airport capacity
--@

CREATE TABLE Airport (
    "airport"       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,  --@ The unique identifier of the airport
    "x"             NUMERIC NOT NULL DEFAULT 0,  --@ x coordinate of the airport. Automatically added by Polaris
    "y"             NUMERIC NOT NULL DEFAULT 0,  --@ y coordinate of the airport. Automatically added by Polaris
    "name"          TEXT    NOT NULL,  --@ Name of the airport, as commonly known
    "capacity"      NUMERIC NOT NULL DEFAULT 0  --@ Annual landed weights of the airport (units: metric tons)
);

SELECT AddGeometryColumn( 'Airport', 'geo', SRID_PARAMETER, 'POINT', 'XY', 1);
SELECT CreateSpatialIndex( 'Airport' , 'geo' );

CREATE INDEX IF NOT EXISTS "AIRPORT_I" ON "Airport" ("airport");
