-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table is designed to hold the schedule of plans for each physical semaphore.
--@
--@ The purpose of this table to map a phasing scheme (*value_phasing*) and a timing structure (*value_timing*)
--@ for each signal (*object_id*) for each time period extending from *value_start* to *value_end*
--@
--@ For each *object_id*, there should be records covering the entire time from 0:00 to 24:00

create TABLE IF NOT EXISTS Signal_Nested_Records(
    object_id      INTEGER NOT NULL,           --@ signal object (Signal table) that it refers to
    "index"        INTEGER NOT NULL,           --@ index within the signal
    value_start    REAL             DEFAULT 0, --@ signal start time (HH:MM)
    value_end      REAL             DEFAULT 0, --@ signal end time (HH:MM)
    value_timing   INTEGER NOT NULL DEFAULT 0, --@ which timing record (Timing table) to be applied
    value_phasing  INTEGER NOT NULL DEFAULT 0, --@ which phasing configuration (Phase table) to be applied
    
    CONSTRAINT "object_id_fk" FOREIGN KEY("object_id") REFERENCES "Signal"("signal") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS "Signal_nested_records_index_i" ON "Signal_nested_records" ("index");

CREATE INDEX IF NOT EXISTS "Signal_nested_records_object_id_i" ON "Signal_nested_records" ("object_id");

CREATE UNIQUE INDEX IF NOT EXISTS Signal_nested_records_unique  ON Signal_nested_records (object_id, "index", value_start, value_end);