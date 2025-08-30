-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table includes the attributes of all ports 
--@ where international shipment goods exit or enter the 
--@ modelled city, including the port name, county,
--@ geographic information, and annual import and export weights
--@

CREATE TABLE International_Port (
    "international_port"       INTEGER NOT NULL  PRIMARY KEY,  --@ The unique identifier of the port
    "name"                     TEXT    NOT NULL,  --@ Name of the port, as commonly known
    "county"                   INTEGER NOT NULL DEFAULT 0,  --@ The county FIPS code of the port
    "x"                        NUMERIC NOT NULL DEFAULT 0,  --@ x coordinate of the port. Automatically added by Polaris
    "y"                        NUMERIC NOT NULL DEFAULT 0,  --@ y coordinate of the port. Automatically added by Polaris
    "imports"                  NUMERIC NOT NULL DEFAULT 0,  --@ Annual import weights of the port (units: metric tons)
    "exports"                  NUMERIC NOT NULL DEFAULT 0,  --@ Annual export weights of the port (units: metric tons)
    "is_rail"                  BOOLEAN NOT NULL DEFAULT 1,  --@ If the international port is available for rail mode
    "is_air"                   BOOLEAN NOT NULL DEFAULT 1   --@ If the international port is available for air mode
);

SELECT AddGeometryColumn( 'International_Port', 'geo', SRID_PARAMETER, 'POINT', 'XY', 1);
SELECT CreateSpatialIndex( 'International_Port' , 'geo' );

CREATE INDEX IF NOT EXISTS "INTERNATIONAL_PORT_I" ON "International_Port" ("international_port");