-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Transit_Vehicle_links logs all the links traversed by a transit vehicle when completing a transit trip
--@
--@

CREATE TABLE "Transit_Vehicle_links" (
  "object_id" INTEGER NOT NULL,                                     --@ The Transit_Vehicle whose trajectory is being described (foreign key to the Transit_Vehicle table)
  "index" INTEGER NOT NULL,                                         --@ Position of link in trajectory
  "value_transit_vehicle_trip" INTEGER NOT NULL DEFAULT 0,          --@ Duplicative to object_id - TODO REMOVE
  "value_transit_vehicle_stop_sequence" INTEGER NOT NULL DEFAULT 0, --@ Duplicative to index - TODO REMOVE
  "value_link" INTEGER NOT NULL DEFAULT 0,                          --@ The link which makes up this part of the overall path (foreign key to Link table)
  "value_dir" INTEGER NOT NULL,                                     --@ The direction of travel on the link {0: a->b, 1: b->a}
  "value_link_type" INTEGER NOT NULL DEFAULT 0,                     --@ Link type as defined by enum. !Link_Type_Keys!
  "value_Est_Arrival_Time" INTEGER NOT NULL DEFAULT 0,              --@ Estimated arrival time of vehicle at link in seconds (units: seconds)
  "value_Act_Arrival_Time" INTEGER NOT NULL DEFAULT 0,              --@ Actual arrival time of vehicle at link in seconds (units: seconds)
  "value_Est_Departure_Time" INTEGER NOT NULL DEFAULT 0,            --@ Estimated departure time of vehicle at link in seconds (units: seconds)
  "value_Act_Departure_Time" INTEGER NOT NULL DEFAULT 0,            --@ Actual departure time of vehicle at link in seconds (units: seconds)
  "value_Est_Dwell_Time" REAL NULL DEFAULT 0,                       --@ Estimated time in seconds spent waiting at stop (units: seconds)
  "value_Act_Dwell_Time" REAL NULL DEFAULT 0,                       --@ Actual time in seconds spent waiting at stop (units: seconds)
  "value_Est_Travel_Time" REAL NULL DEFAULT 0,                      --@ Estimated travel time in seconds to traverse link (units: seconds)
  "value_Act_Travel_Time" REAL NULL DEFAULT 0,                      --@ Actual travel time in seconds to traverse link (units: seconds)
  "value_Boardings" INTEGER NOT NULL DEFAULT 0,                     --@ Number of traveler boardings logged by vehicle on this trip
  "value_Alightings" INTEGER NOT NULL DEFAULT 0,                    --@ Number of traveler alightings logged by vehicle on this trip
  "value_Seated_Load" INTEGER NOT NULL DEFAULT 0,                   --@ Number of seated occupants while vehicle traversed this link
  "value_Seated_Capacity" INTEGER NOT NULL DEFAULT 0,               --@ Number of total seats available
  "value_Standing_Load" INTEGER NOT NULL DEFAULT 0,                 --@ Number of standing occupants while vehicle traversed this link
  "value_Standing_Capacity" INTEGER NOT NULL DEFAULT 0,             --@ Total standing space available in number of persons
  "value_start_position" REAL NULL DEFAULT 0,                       --@ Cumulative value in meters of distance traversed in trajectory as logged at beginning of link (units: meters)
  "value_exit_position" REAL NULL DEFAULT 0,                        --@ Cumulative value in meters of distance traversed in trajectory as logged at end of link (units: meters)
  "value_length" REAL NULL DEFAULT 0,                               --@ Lenght of link in meters (units: meters)
  "value_speed" REAL NULL DEFAULT 0,                                --@ Speed that vehicle traversed the link for this trip in meters per second (units: m/s)
  CONSTRAINT "object_id_fk"
    FOREIGN KEY ("object_id")
    REFERENCES "Transit_Vehicle" ("transit_vehicle_trip")
    ON DELETE CASCADE)