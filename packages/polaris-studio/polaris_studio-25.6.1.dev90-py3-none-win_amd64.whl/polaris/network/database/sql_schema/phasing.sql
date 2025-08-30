-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Each record on this table corresponds to a full semaphore phase detailed on Phasing_Nested_Records.
--@ the field *signal* associates the phasing plan with a physical signalized intersection, while the field
--@ *phasing* groups phase into a single phasing plan, with the field *phase* dictating their order and the
--@ field *movements* representing a simple count of the movements allowed in that semaphore phase.
--@
--@ The phasing_id field in this table is defined as 100 * node_id + 10 * period index + phase_index

create TABLE IF NOT EXISTS Phasing(
    phasing_id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ phasing identifier
    signal        INTEGER,                     --@ signal (from table signal) that this semaphore phase refers to
    phasing       INTEGER NOT NULL DEFAULT 0,  --@ index of phasing configuration
    phase         INTEGER NOT NULL DEFAULT 0,  --@ phase within the phase configuration
    movements     INTEGER NOT NULL DEFAULT 0,  --@ number of movements within the phase (set by POLARIS)

    CONSTRAINT "signal_fk" FOREIGN KEY("signal") REFERENCES "Signal"("signal") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);


create INDEX IF NOT EXISTS "Phasing_signal_i" ON "Phasing" ("signal");
create INDEX IF NOT EXISTS "Phasing_timing_i" ON "Phasing" ("phasing");
