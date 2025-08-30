-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Table contains records of every maintenance and cleaning activity for shared vehicles during simulation.
--@ Records in this table is typically not generated and needs to be turned on for the fleet within the fleet model file.
--@

CREATE TABLE "TNC_Servicing" (
  "Station_ID" INTEGER NULL DEFAULT 0,             --@ Service station ID where maintenance or cleaning was performed. Currently the same as an EV_Charging_Station.
  "Latitude" REAL NULL DEFAULT 0,                  --@ Latitude of the station in degrees. To be converted to meters soon.
  "Longitude" REAL NULL DEFAULT 0,                 --@ Longitude of the station in degrees. To be converted to meters soon.
  "vehicle" INTEGER NULL,                          --@ Vehicle that underwent maintenance and/or cleaning  (foreign key to the Vehicle table)
  "Time_In" INTEGER NOT NULL DEFAULT 0,            --@ The time at which the vehicle reached the service station. (units: seconds)
  "Time_Start" INTEGER NOT NULL DEFAULT 0,         --@ The time at which the maintenance/cleaning operation began. (units: seconds)
  "Time_Out" INTEGER NOT NULL DEFAULT 0,           --@ The time at which the maintenance/cleaning operation ended. (units: seconds)
  "Location_Type" TEXT NOT NULL DEFAULT '',        --@ Location type - possible values are {"Station"}
  "Is_TNC_Vehicle" INTEGER NOT NULL DEFAULT 0,     --@ boolean flag - is the TNC vehicle being serviced a TNC vehicle. Should always be true at the moment.
  "Is_Cleaning_Only" INTEGER NOT NULL DEFAULT 0,   --@ boolean flag - is the activity is cleaning only? (includes maintenance if false)
  "Is_Artificial_Move" INTEGER NOT NULL DEFAULT 0, --@ boolean flag - did the EV arrive at the station without sufficient battery. Will be removed.

  CONSTRAINT "vehicle_fk"
    FOREIGN KEY ("vehicle")
    REFERENCES "Vehicle" ("vehicle_id")
    DEFERRABLE INITIALLY DEFERRED)