-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ An output table for activities a person perticipates in.
--@ Note this table contains both palnned activities which are not assigned to the network yet (trip == 0)
--@ as well as assigned activities (trip > 0).

CREATE TABLE "Activity" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ Unique identifier of this activity
  "seq_num" INTEGER NOT NULL DEFAULT 0,            --@ Order in which activities were generated per person; note home activities are +=100 and split activities +=1000
  "location_id" INTEGER NOT NULL DEFAULT 0,        --@ Location at which this activity took place (foreign key to the Location table)
  "start_time" REAL NULL DEFAULT 0,                --@ Simulation time in seconds when this activity starts (units: seconds)
  "duration" REAL NULL DEFAULT 0,                  --@ Duration of the activity in seconds of simulation time (units: seconds)
  "mode" TEXT NOT NULL DEFAULT '',                 --@ Mode to reach this activity, possible values are keys in !Vehicle_Type_Keys!
  "type" TEXT NOT NULL DEFAULT '',                 --@ Type of the activity, possible values are keys in !ACTIVITY_TYPES!
  "person" INTEGER NOT NULL,                       --@ Person undertaking this activity (foreign key to the Person table)
  "trip" INTEGER NOT NULL,                         --@ The trip which was used to reach this activity (foreign key to trip table); 0 indicates this is a planned activity without trip
  "origin_id" INTEGER NOT NULL DEFAULT 0,          --@ The location of the previous activity (foreign key to the Location table)

  CONSTRAINT "person_fk"
    FOREIGN KEY ("person")
    REFERENCES "Person" ("person")
    DEFERRABLE INITIALLY DEFERRED)