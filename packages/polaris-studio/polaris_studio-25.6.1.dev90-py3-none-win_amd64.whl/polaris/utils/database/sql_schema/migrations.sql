-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table holds metadata about which upgrades have been applied to the
--@ data structures in this database. It is used by the polaris-studio migration manager
--@ to determine the current state of the database and the pathway to upgrading 
--@ the database to align with POLARIS requirements.
--@

CREATE TABLE IF NOT EXISTS "Migrations" (
    "migration_id"  TEXT NOT NULL UNIQUE,  --@ unique identifier which corresponds to a python or sql migration file in polaris-studio
    "description"  TEXT,                   --@ human readable description of the migration
    "applied_at"    TEXT NOT NULL          --@ when this migration was applied to this database
);


CREATE UNIQUE INDEX IF NOT EXISTS Migration_record ON "Migrations" ("migration_id");