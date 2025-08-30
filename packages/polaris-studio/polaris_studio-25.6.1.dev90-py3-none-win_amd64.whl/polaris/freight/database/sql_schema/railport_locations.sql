-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Railport Locations table
--@ mainly contains the location of railport
--@

CREATE TABLE Railport_Locations (
    "railport"  INTEGER NOT NULL DEFAULT 0,  --@ The unique identifier of the railport as in Railport table
    "location"  INTEGER NOT NULL DEFAULT 0,  --@ The selected location of the railports (From the Supply Location table)

    CONSTRAINT railport_loc_fk FOREIGN KEY (railport)
    REFERENCES Railport (railport) DEFERRABLE INITIALLY DEFERRED
);
