-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ List of Point of Entry for trucks by OD pair between all counties in the model and external counties
--@

CREATE TABLE Truck_Poe (
    "internal_county" INTEGER NOT NULL DEFAULT 0,  --@ ID of the county inside the modelled area
    "external_county" INTEGER NOT NULL DEFAULT 0,  --@ ID of the county outside the modelled area
    "location"        INTEGER NOT NULL DEFAULT 0   --@ ID of the location in the Supply file
);
