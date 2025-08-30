-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all micro-mobility operators available in the model
--@
--@ The operator-id functions like the agency_id for public transport agencies
--@ and pre-fixes some fields in other related tables
--@
create TABLE IF NOT EXISTS Micromobility_Agencies(
    agency      TEXT    NOT NULL,                           --@ Name of the micromobility agency
    agency_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ The unique identifier of the micromobility agency
    description TEXT                                        --@ A text based description of the agency (optional)
);

create UNIQUE INDEX IF NOT EXISTS micro_operators_id ON Micromobility_Agencies (agency_id);