-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table holds metadata about the freight model data, it has the same structure
--@ as the similarly named tables in the network/demands databases.
--@
--@ This table can be read and written by the read_about_model and write_about_model 
--@ methods in polaris-studio.

CREATE TABLE IF NOT EXISTS "About_Model" (
    "infoname"  TEXT NOT NULL PRIMARY KEY,  --@ The key used to look up metadata (i.e. "build-date")
    "infovalue" TEXT NOT NULL DEFAULT ''    --@ The value (actual data) (i.e. "2024-01-24")
);
