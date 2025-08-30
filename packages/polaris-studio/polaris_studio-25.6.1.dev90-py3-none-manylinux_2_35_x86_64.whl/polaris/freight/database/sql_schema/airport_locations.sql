-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This Airport Point of Entry (POE) Locations table
--@ mainly contains the location of airport
--@

CREATE TABLE Airport_Locations (
    "airport"       INTEGER NOT NULL DEFAULT 0, --@ The unique identifier of the airport as in the Airport table
    "location"      INTEGER NOT NULL DEFAULT 0,  --@ The selected location of the airport (foreign key to the Location table)

    CONSTRAINT airportloc_fk FOREIGN KEY (airport)
    REFERENCES Airport (airport) DEFERRABLE INITIALLY DEFERRED
);