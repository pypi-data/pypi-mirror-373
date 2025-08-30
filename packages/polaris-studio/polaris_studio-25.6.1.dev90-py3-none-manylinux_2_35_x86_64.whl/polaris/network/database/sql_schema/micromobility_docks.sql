-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all micromobility docks available in the model
--@
--@ Critical fields here are the operator and the number of regular and charging docks
--@
CREATE TABLE IF NOT EXISTS Micromobility_Docks(
    dock_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    agency_id       INTEGER NOT NULL,
    link            INTEGER,
    dir             INTEGER,
    offset          REAL,
    setback         REAL,
    x               REAL    NOT NULL DEFAULT 0,
    y               REAL    NOT NULL DEFAULT 0,
    z               REAL    NOT NULL DEFAULT 0,
    zone            INTEGER,
    regular_docks   INTEGER NOT NULL DEFAULT 0,
    charging_docks  INTEGER NOT NULL DEFAULT 0,
    name          TEXT,
    has_parking     INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY(agency_id) REFERENCES Micromobility_Agencies(agency_id) deferrable initially deferred,
    FOREIGN KEY("zone") REFERENCES "Zone"("zone") deferrable initially deferred
);

select AddGeometryColumn( 'Micromobility_Docks', 'geo', SRID_PARAMETER, 'POINT', 'XY', 1);

select CreateSpatialIndex( 'Micromobility_Docks' , 'geo' );
