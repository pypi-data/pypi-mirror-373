-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table contains the individual records of timing for each signal phase,
--@ and connects to the timing ID through its object_id. In this sense, there
--@ is no unique identifier in this table, as a single record does not mean much.

create TABLE IF NOT EXISTS Timing_Nested_Records(
    object_id         INTEGER NOT NULL,           --@ timing id that it refers to
    "index"           INTEGER NOT NULL,           --@ index within the timing id
    value_phase       INTEGER NOT NULL DEFAULT 0, --@ referred phase
    value_barrier     INTEGER NOT NULL DEFAULT 0, --@ not used currently in POLARIS
    value_ring        INTEGER NOT NULL DEFAULT 0, --@ not used currently in POLARIS
    value_position    INTEGER NOT NULL DEFAULT 0, --@ similar as index, currently not used
    value_minimum     INTEGER NOT NULL DEFAULT 0, --@ minimum green time (for fixed time set min=max=green time)
    value_maximum     INTEGER NOT NULL DEFAULT 0, --@ maximum green time (for fixed time set min=max=green time)
    value_extend      INTEGER NOT NULL DEFAULT 0, --@ green extension for actuated phase
    value_yellow      INTEGER NOT NULL DEFAULT 0, --@ yellow time
    value_red         INTEGER NOT NULL DEFAULT 0, --@ all red time

    CONSTRAINT "object_id_fk" FOREIGN KEY("object_id") REFERENCES "Timing"("timing_id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS "Timing_nested_records_index_i" ON "Timing_nested_records" ("index");
CREATE INDEX IF NOT EXISTS "Timing_nested_records_object_id_i" ON "Timing_nested_records" ("object_id");
