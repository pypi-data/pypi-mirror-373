-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The NAICS-Landuses table show a crosswalk between the NAICS
--@ industry sector and possible landuses for each sector

CREATE TABLE Naics_Landuses (
    "naics"         INTEGER NOT NULL,   --@ A 3-digit NAICS code from the modelled sectors
    "land_use"      TEXT    NOT NULL DEFAULT "ALL"   --@ Text describing the land use type represented by this location. !LAND_USE!
);
