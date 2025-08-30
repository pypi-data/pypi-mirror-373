-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The TNC_Trip table stores all trips made by shared mobility vehicles - referred to here as TNC vehicles.
--@ Each record in the table includes a leg of travel - either pickup, dropoff, charging, or repositioning.
--@ Several records together for a specific vehicle may form a tour, meaning the vehicle was continuously in operation
--@ from one trip to the next, without a break.

CREATE TABLE "TNC_Trip" (
  "TNC_trip_id_int" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ Integerized trip ID for each TNC_Trip record
  "TNC_trip_id" INTEGER NOT NULL,            --@ Not used
  "path" INTEGER NOT NULL DEFAULT -1,        --@ Path ID is not -1 if there exists Path-related information in the Path table (in H5) referenced by this value (foreign key to the Path table)
  "path_multimodal" INTEGER NULL,            --@ All TNC trips are on auto network, so no multimodal travel information is logged Always NULL
  "tour" INTEGER NOT NULL DEFAULT 0,         --@ Counter for tours that are formed from a series of continuous trips undertaken by the TNC vehicle
  "start" REAL NULL DEFAULT 0,               --@ Time at which the TNC vehicle started its trip (units: seconds)
  "end" REAL NULL DEFAULT 0,                 --@ Time at which the TNC vehicle ended its trip (units: seconds)
  "duration" REAL NULL DEFAULT 0,            --@ Not used
  "origin" INTEGER NOT NULL DEFAULT 0,       --@ Origin location of the trip (foreign key to the Location table)
  "destination" INTEGER NOT NULL DEFAULT 0,  --@ Destination location of the trip (foreign key to the Location table)
  "purpose" INTEGER NOT NULL DEFAULT 0,      --@ Not used
  "mode" INTEGER NOT NULL DEFAULT 0,         --@ The mode of the trip !Vehicle_Type_Keys! should always be 9: "TAXI/TNC"
  "type" INTEGER NOT NULL DEFAULT 0,         --@ Trip type as defined in !Trip_Types!, should always be ABM
  "vehicle" INTEGER NULL,                    --@ TNC vehicle ID associated with the trip (foreign key to the Vehicle table)
  "passengers" INTEGER NOT NULL DEFAULT 0,   --@ Number of passengers on board the TNC vehicle during the execution of the trip recorded
  "travel_distance" REAL NULL DEFAULT 0,     --@ Distance traveled during the trip (units: meters)
  "skim_travel_time" REAL NULL DEFAULT 0,    --@ Travel time from the skim table for comparison with execution (units: seconds)
  "routed_travel_time" REAL NULL DEFAULT 0,  --@ Travel time from the router for comparison with execution (units: seconds)
  "request_time" REAL NULL DEFAULT 0,        --@ Simulation time when the request being served actually requested that trip (units: seconds)
  "init_status" INTEGER NOT NULL DEFAULT 0,  --@ TNC status denoting what operation was being done when trip started. Allowable values are: Pickup (-1), Dropoff (-2), (-3), Repositioning (-3), and Charging (-4)
  "final_status" INTEGER NOT NULL DEFAULT 0, --@ TNC status denoting what operation was actually done when trip ended because of mid-trip detours. Allowable values are: Pickup (-1), Dropoff (-2), Repositioning (-3), and Charging (-4)
  "init_battery" REAL NULL DEFAULT 0,        --@ If electric vehicle, battery state of charge at the beginning of the trip (units: %)
  "final_battery" REAL NULL DEFAULT 0,       --@ If electric vehicle, battery state of charge at the end of the trip (units: %)
  "fare" REAL NULL DEFAULT 0,                --@ Fare collected from executing this leg of the trip - Not to be used - Use fare from TNC_Request instead.
  "person" INTEGER NULL,                     --@ If request is related to a person, then the person ID is logged (foreign key to the Person table)
  "request" INTEGER NOT NULL DEFAULT 0,      --@ Request object which tracks additional details of the request that generated this trip  (foreign key to the TNC_Request table)
  "toll" REAL NOT NULL DEFAULT 0.0,          --@ Toll paid in executing the trip (units: $USD)
  "has_artificial_trip" INTEGER NOT NULL DEFAULT 0,   --@ Denotes the type of artificial trip and can include values in !Artificial_Trip_Reasons!

  CONSTRAINT "vehicle_fk"
    FOREIGN KEY ("vehicle")
    REFERENCES "Vehicle" ("vehicle_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "person_fk"
    FOREIGN KEY ("person")
    REFERENCES "Person" ("person")
    DEFERRABLE INITIALLY DEFERRED)