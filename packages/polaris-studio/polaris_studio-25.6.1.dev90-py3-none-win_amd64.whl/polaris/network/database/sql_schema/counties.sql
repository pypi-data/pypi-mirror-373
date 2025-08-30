-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all Counties covered by the model area

CREATE TABLE IF NOT EXISTS Counties(
    county                   INTEGER NOT NULL              PRIMARY KEY, --@ County FIPS code
    x                        REAL    NOT NULL    DEFAULT 0, --@ X coordinate of the county centroid. Automatically added by Polaris.
    y                        REAL    NOT NULL    DEFAULT 0, --@ Y coordinate of the county centroid. Automatically added by Polaris.
    name                     TEXT, --@ County name
    statefp                  TEXT, --@ two-digit state FP
    state                    TEXT --@ two-digit state abbreviation
);

SELECT AddGeometryColumn( 'Counties', 'geo', SRID_PARAMETER, 'MULTIPOLYGON', 'XY' );
SELECT CreateSpatialIndex( 'Counties' , 'geo' );

CREATE INDEX IF NOT EXISTS "IDX_COUNTIES_COUNTY" ON "Counties" ("county");
