-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Person_Gaps table holds the status of assignment at the person level.
--@ As we are using agent-specific routers and agent-based dynamic equilibrium, the
--@ gaps stored here can help with convergence.
--@
--@ Not currently used, but logged.

CREATE TABLE "Person_Gaps" (
  "person" INTEGER NOT NULL PRIMARY KEY, --@ The person whose average gap is being logged (foreign key to Person table)
  "avg_gap" REAL NULL DEFAULT 0,         --@ Float value of gap estimated based on routed travel time and estimated travel time.
  
  CONSTRAINT "person_fk"
    FOREIGN KEY ("person")
    REFERENCES "Person" ("person")
    DEFERRABLE INITIALLY DEFERRED)