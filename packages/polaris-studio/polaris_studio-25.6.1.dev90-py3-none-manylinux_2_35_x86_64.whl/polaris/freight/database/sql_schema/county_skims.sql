-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The county skims table contains the travel distance 
--@ between each of the counties within the modelled region. 
--@ It is used by the CRISTAL freight model for high-level
--@ movement synthesis.
--@

CREATE TABLE IF NOT EXISTS "County_Skims" (
    "county_orig" INTEGER NOT NULL DEFAULT 0, --@ The origin county FIPS code
    "county_dest" INTEGER NOT NULL DEFAULT 0, --@ The destination county FIPS code
    "gcd_miles"   REAL             DEFAULT 0, --@ The great circle distance between the two counties (units: miles)
    "hwy_miles"   REAL             DEFAULT 0  --@ The shortest routable highway distance between the two counties (units: miles)
);
