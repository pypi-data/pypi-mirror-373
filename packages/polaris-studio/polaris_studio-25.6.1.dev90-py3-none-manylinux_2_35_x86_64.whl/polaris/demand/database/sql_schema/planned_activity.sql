-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ An output table for planned activites a person wants to participate in.
--@ Note this is a debug table and records activity attributes at the time of planning
--@ in activity generation. As such it will only be populated if write_planned_activity_table is set to true.

CREATE TABLE "Planned_Activity" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ Unique identifier of this activity
  "seq_num" INTEGER NOT NULL DEFAULT 0,            --@ Order in which activities were generated per person; note home activities are +=100 and split activities +=1000
  "location_id" INTEGER NOT NULL DEFAULT 0,        --@ Location of the activity (foreign key to the Location table)
  "start_time" REAL NULL DEFAULT 0,                --@ Start time of the activity at the time of planning (units: seconds)
  "duration" REAL NULL DEFAULT 0,                  --@ Duration of the activity at the time of planning (units: seconds)
  "mode" TEXT NOT NULL DEFAULT '',                 --@ Mode to reach this activity at the time of planning, possible values are keys in !Vehicle_Type_Keys!
  "type" TEXT NOT NULL DEFAULT '',                 --@ Type of the activity, possible values are keys in !ACTIVITY_TYPES!
  "person" INTEGER NOT NULL,                       --@ The person undertaking this activity (foreign key to the Person table)
  "trip" INTEGER NOT NULL,                         --@ Always 0
  "origin_id" INTEGER NOT NULL DEFAULT 0,          --@ Location of previous activity at the time of planning (foreign key to the Location table)
  "status" INTEGER NOT NULL DEFAULT 0,             --@ Planning status. 0 means added to schedule, larger than zero indicates planning failure and activity is dropped
  "plan_time" INTEGER NOT NULL DEFAULT 0,          --@ Simulation time when activity is scheduled (units: seconds)

  CONSTRAINT "person_fk"
    FOREIGN KEY ("person")
    REFERENCES "Person" ("person")
    DEFERRABLE INITIALLY DEFERRED)