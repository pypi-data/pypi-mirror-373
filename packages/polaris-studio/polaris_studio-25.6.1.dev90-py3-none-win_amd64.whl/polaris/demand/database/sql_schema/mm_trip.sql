-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Table demostrates travelers' micromobility trip attributes. It includes origin, destination, path, travel time, etc. attributes of the trip.
--@
--@

CREATE TABLE "MM_Trip" (
  "MM_trip_id_int" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ The unique identifier for the micromobility trip
  "MM_trip_id" INTEGER NOT NULL,            --@ Duplicative and unused. Will be removed.
  "path" INTEGER NULL,                      --@ All MM trips are on bike network, is in the Path table referenced by this ID.
  "path_multimodal" INTEGER NULL,           --@ Always NULL because info is logged in the Path table.
  "start" REAL NULL DEFAULT 0,              --@ Start time of the trip (units: seconds)
  "end" REAL NULL DEFAULT 0,                --@ End time of the trip (units: seconds)
  "origin" INTEGER NOT NULL DEFAULT 0,      --@ Trip origin location identifier (foreign key to Location table)
  "destination" INTEGER NOT NULL DEFAULT 0, --@ Trip destination location identifier (foreign key to Location table)
  "mode" INTEGER NOT NULL DEFAULT 0,        --@ The mode utilised for this trip !Vehicle_Type_Keys!
  "type" INTEGER NOT NULL DEFAULT 0,        --@ What type of trip is this !Trip_Types!
  "vehicle" INTEGER NULL,                   --@ Micromobility vehicle identifier (foreign key to Vehicle table)
  "travel_distance" REAL NULL DEFAULT 0,    --@ Travelled distance of the trip (units: meters)
  "skim_travel_time" REAL NULL DEFAULT 0,   --@ Expected travel time at the start of the trip - from skim (units: seconds)
  "routed_travel_time" REAL NULL DEFAULT 0, --@ Actual routed travel time of the trip (units: seconds)
  "status" INTEGER NOT NULL DEFAULT 0,      --@ Micromobility vehicle status denoting what operation was being done when trip started. !MM_Status!
  "person" INTEGER NULL,                    --@ The unique identifier for the individual making the trip (foreign key to Person table)

  CONSTRAINT "vehicle_fk"
    FOREIGN KEY ("vehicle")
    REFERENCES "Vehicle" ("vehicle_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "person_fk"
    FOREIGN KEY ("person")
    REFERENCES "Person" ("person")
    DEFERRABLE INITIALLY DEFERRED)