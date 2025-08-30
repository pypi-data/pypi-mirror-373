-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table includes the locations of internal ports 
--@ that are within the modelled city
--@

CREATE TABLE International_Port_Locations (
    "international_port"       INTEGER NOT NULL DEFAULT 0, --@ The unique identifier of the port as in the International_Port table
    "location"                 INTEGER NOT NULL DEFAULT 0, --@ The selected location of the internal port (foreign key to the Location table)

    CONSTRAINT internationalportloc_fk FOREIGN KEY (international_port)
    REFERENCES International_Port (international_port) DEFERRABLE INITIALLY DEFERRED
);