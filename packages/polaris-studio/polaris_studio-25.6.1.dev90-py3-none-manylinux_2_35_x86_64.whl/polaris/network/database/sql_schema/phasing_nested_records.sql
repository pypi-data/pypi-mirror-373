-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Each *object_id* corresponds to one phase of a semaphore plan, and it is composed of n movements numbered from
--@ 0 to n-1. *value_movement* identifies the movement geometrically, while *value_link*, *dir*, *value_to_link*
--@ identifies a unique connection. The field value_protect identifies the type of movement, if **PROTECTED**,
--@ **STOP_PERMIT** or **PERMITTED**.
--@
--@ In reality, this table describes each phase of each signal identified by their *object_id*, but in this fashion
--@ it allows for multiple phase configurations for each intersection. The identification of a unique semaphore
--@ plan is only possible when analyzing the table **Phasing**.

create TABLE IF NOT EXISTS Phasing_Nested_Records(
    object_id         INTEGER NOT NULL,            --@ phasing record the nested record refers to
    "index"           INTEGER NOT NULL,            --@ index within the same object_id of nested records
    value_movement    TEXT    NOT NULL DEFAULT '', --@ movement type (SB_LEFT, NB_LEFT, etc.)
    value_link        INTEGER,                     --@ the bidirectional link in which it refers to
    value_dir         INTEGER NOT NULL DEFAULT 0,  --@ direction (0 for AB, 1 for BA) within the link
    value_to_link     INTEGER,                     --@ the downstream link
    value_protect     TEXT    NOT NULL DEFAULT '', --@ right of way information (PROTECTED, STOP_PERMIT, PERMITTED)

    CONSTRAINT "object_id_fk" FOREIGN KEY("object_id") REFERENCES "Phasing"("phasing_id") ON DELETE CASCADE,
    CONSTRAINT "value_to_link_fk" FOREIGN KEY("value_to_link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "value_link_fk" FOREIGN KEY("value_link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "Phasing_nested_records_index_i" ON "Phasing_nested_records" ("index");
CREATE INDEX IF NOT EXISTS "Phasing_nested_records_object_id_i" ON "Phasing_nested_records" ("object_id");
CREATE UNIQUE INDEX IF NOT EXISTS "PNR_uniqueness" ON "Phasing_nested_records" (object_id, value_link, value_to_link);
CREATE UNIQUE INDEX IF NOT EXISTS "PNR_unique" ON "Phasing_nested_records" (object_id, value_to_link, value_protect);
