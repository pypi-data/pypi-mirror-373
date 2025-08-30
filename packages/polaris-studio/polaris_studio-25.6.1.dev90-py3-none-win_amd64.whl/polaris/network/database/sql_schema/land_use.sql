-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table lists all land uses that may be attributed to Locations
--@
--@ Properly setting the flags is_home, is_work and is_discretionary
--@ is absolutely CRITICAL for the correct performance of Polaris.


create TABLE IF NOT EXISTS Land_Use(
    land_use              TEXT    NOT NULL PRIMARY KEY, --@ Text description of the land use type - corresponds to the enums defined in Activity_Location_Components::Types::LAND_USE
    is_home               INTEGER NOT NULL DEFAULT 0,   --@ Dummy variable, 1 if the type of land use is single detached or - residential property, 0 otherwise
    is_work               INTEGER NOT NULL DEFAULT 0,   --@ Dummy variable, 1 if the type of land use is any property except single detached and/or multi-unit residential property, 0 otherwise
    is_school             INTEGER NOT NULL DEFAULT 0,   --@ Dummy variable, 1 if the type of land use is any educational or higher educational institute
    is_discretionary      INTEGER NOT NULL DEFAULT 0,   --@ Dummy variable, 1 if the type of land use is any property except educational or higher educational institute, 0 otherwise
    notes                 TEXT --@

    CHECK(is_home IN (0, 1))
    CHECK(is_work IN (0, 1))
    CHECK(is_school IN (0, 1))
    CHECK(is_discretionary IN (0, 1)));

create INDEX IF NOT EXISTS "idx_land_use" ON "Land_Use" ("land_use");

INSERT INTO "Land_Use" VALUES ('ALL',1,1,1,1,NULL);
