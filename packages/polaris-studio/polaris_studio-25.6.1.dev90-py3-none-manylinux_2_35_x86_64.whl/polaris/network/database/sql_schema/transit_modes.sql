-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table provides a mapping from GTFS modes to human readable labels and provides assumptions on standard
--@ operating costs by mode.
--@

CREATE TABLE IF NOT EXISTS Transit_Modes(
    mode_id                 INTEGER PRIMARY KEY, --@ Mode ID as defined in GTFS
    mode_name               TEXT NOT NULL,       --@ Human readable mode name
    operating_cost_per_hour REAL NOT NULL        --@ Operating cost per hour in dollars
);