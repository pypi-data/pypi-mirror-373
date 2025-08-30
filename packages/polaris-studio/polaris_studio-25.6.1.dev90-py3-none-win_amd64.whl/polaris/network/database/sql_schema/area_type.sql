-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Area types are used throughout the demand model to differentiate different
--@ regions within the modeled area (e.g. CBD, inner suburb, outer suburb,
--@ industrial).
--@
--@ Values for area_type are fixed and in the set (1,2,3,4,5,6,7,8,98,99), and
--@ Polaris models have particular parameters for these area types. Do not change them without being certain of it.

create TABLE IF NOT EXISTS Area_Type(
    area_type INTEGER NOT NULL PRIMARY KEY, --@ Unique identifier for the area type
    name      TEXT    NOT NULL DEFAULT '',  --@ Simple description of the area type
    notes     TEXT                          --@ User notes
);