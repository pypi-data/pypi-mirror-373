-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Incidents to be applied during the simulation (only supported in Mesoscopic model)

CREATE TABLE IF NOT EXISTS Traffic_Incident(
    link           INTEGER NOT NULL,           --@ link in which the incident applies
    dir            INTEGER NOT NULL DEFAULT 0, --@ direction (0 for A to B, 1 from B to A)
    start_time     INTEGER NOT NULL DEFAULT 0, --@ initial time (in seconds from midnight) in which the incident occurs
    end_time       INTEGER NOT NULL DEFAULT 0, --@ final time (in seconds from midnight) in which the incident occurs
    capacity_scale REAL    NOT NULL DEFAULT 0, --@ relative capacity that the link will experience from 0 (completely blocked) to 1 (no impact)
    
    CONSTRAINT "link_fk" FOREIGN KEY ("link") REFERENCES "Link" ("link") DEFERRABLE INITIALLY DEFERRED -- check
);