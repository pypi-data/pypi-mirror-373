-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ List of rail operators in the model
--@

CREATE TABLE Rail_Operator (
    "rail_operator" INTEGER NOT NULL PRIMARY KEY, --@ The unique identifier of the rail operator
    "name"          TEXT    NOT NULL,             --@ Name of the rail operator
    "short_name"    TEXT    NOT NULL              --@ Rail operator acronym
);

CREATE INDEX IF NOT EXISTS "rail_operator_i" ON "Rail_Operator" ("rail_operator");
