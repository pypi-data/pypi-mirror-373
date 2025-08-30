-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all population synthesis regions used in the model. These are the areas at which Polaris will perform population synthesis
--@ And must correspond exactly to the popsyn region identifiers shown in the sf1 file in your model's folder structure.

CREATE TABLE IF NOT EXISTS PopSyn_Region(
    popsyn_region INTEGER NOT NULL PRIMARY KEY --@ ID for the popsyn region, could be census tract, block group or group or any custom spatial identifier
);

SELECT AddGeometryColumn( 'PopSyn_Region', 'geo', SRID_PARAMETER, 'MULTIPOLYGON', 'XY', 1);
SELECT CreateSpatialIndex( 'PopSyn_Region' , 'geo' );

CREATE INDEX IF NOT EXISTS "IDX_POPSYN_REGION_COUNTY" ON "PopSyn_Region" ("popsyn_region");
