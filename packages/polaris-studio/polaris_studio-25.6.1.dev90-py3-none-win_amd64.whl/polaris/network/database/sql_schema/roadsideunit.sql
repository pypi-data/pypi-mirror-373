-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
CREATE TABLE IF NOT EXISTS Roadsideunit(
    unit_id                  INTEGER UNIQUE NOT NULL PRIMARY KEY, --@ RSU identifier
    link                     INTEGER        NOT NULL,             --@ bidirectional link where the RSU is
    dir                      INTEGER        NOT NULL DEFAULT 0,   --@ direction (0 for AB, 1 for BA)
    position                 REAL           NOT NULL DEFAULT 0,   --@ position along the link
    power                    REAL           not null DEFAULT 0,   --@ transmission/power capability (currently not used by POLARIS)
    collected_info           TEXT,                                --@ type of data exchanged with vehicles (currently not used by POLARIS)
    Logging_interval_seconds int            not null DEFAULT 0,   --@ data logging interval (currently not used by POLARIS)

    CONSTRAINT "link_fk" FOREIGN KEY ("link") REFERENCES "Link" ("link") DEFERRABLE INITIALLY DEFERRED -- check
);