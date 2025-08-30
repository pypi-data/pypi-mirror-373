-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ List of railports in the model
--@

CREATE TABLE Railport (
    "railport"  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,  --@ The unique identifier of the rail terminal
    "x"         NUMERIC NOT NULL DEFAULT 0,  --@ x coordinate of the terminal
    "y"         NUMERIC NOT NULL DEFAULT 0,  --@ y coordinate of the terminal
    "name"      TEXT    NOT NULL,  --@ Name of the terminal
    "capacity"  REAL    NOT NULL DEFAULT 0  --@ Capacity of the rail terminal (units: Twenty-foot Equivalent Units)
);

SELECT AddGeometryColumn( 'Railport', 'geo', SRID_PARAMETER, 'POINT', 'XY', 1);
SELECT CreateSpatialIndex( 'Railport' , 'geo' );

CREATE INDEX IF NOT EXISTS "Railport_I" ON "Railport" ("railport");
