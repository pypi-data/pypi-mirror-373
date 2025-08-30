-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table holds the list of each unique timing configuration *timing_id* for each signal in the model.
--@
--@ The signal the timing refers to is defined in *signal* and the identifier of the the timing among the other
--@ available for this signal is defined in *timing*.
--@
--@ The field *phases* identifies the number of corresponding records on **Timing_Nested_Records**, where *object_id*
--@ would be equal to this table's *timing_id*.
--@
--@ *cycle* defines the total cycle time for this semaphore timing plan.
--@
--@ For now, *offset* is always equal to 0

create TABLE IF NOT EXISTS Timing(
    timing_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ timing identifier
    signal    INTEGER,                          --@ signal (Signal table) which this timing refers to
    timing    INTEGER NOT NULL DEFAULT 0,       --@ index of the timing (within the same signal) of the timing
    "type"    TEXT    NOT NULL DEFAULT "TIMED", --@ type (TIMED, ACTUATED). Generally TIMED is used
    cycle     INTEGER NOT NULL DEFAULT 0,       --@ cycle time (SET by POLARIS as the sum of green + inter-greens across all nested records)
    offset    INTEGER NOT NULL DEFAULT 0,       --@ timing offset (applied based on cycle and start_time in signal table)
    phases    INTEGER NOT NULL DEFAULT 0,       --@ number of phases (set by POLARIS)

    CONSTRAINT "signal_fk" FOREIGN KEY("signal") REFERENCES "Signal"("signal") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "Timing_signal_i" ON "Timing" ("signal");
CREATE INDEX IF NOT EXISTS "Timing_timing_i" ON "Timing" ("timing");
