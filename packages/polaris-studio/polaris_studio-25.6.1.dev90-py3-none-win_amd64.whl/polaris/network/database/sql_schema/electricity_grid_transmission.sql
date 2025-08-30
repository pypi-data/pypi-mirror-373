-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Provides the transmission buses in the region. 
--@ It is linked to A-LEAF by providing aggregating electricity demand to it.
--@
--@ Not required by all models and is okay to be empty.

CREATE TABLE IF NOT EXISTS Electricity_Grid_Transmission(
    Transmission_Bus_ID INTEGER NOT NULL PRIMARY KEY, --@ Primary integer key representing the transmission bus available in the model region
    name                TEXT DEFAULT ''               --@ Text description of the transmission bus ID if one exists
);