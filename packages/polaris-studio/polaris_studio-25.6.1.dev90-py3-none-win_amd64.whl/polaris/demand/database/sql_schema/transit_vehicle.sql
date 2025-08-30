-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Transit_Vehicle tables records all transit vehicles used for carrying out the transit simulation according to the available routes and patterns.
--@
--@

CREATE TABLE "Transit_Vehicle" (
  "transit_vehicle_trip" INTEGER NOT NULL PRIMARY KEY, --@ The trip being carried out by the transit vehicle  (foreign key to the Transit_Vehicle_Trip table)
  "vehicle" INTEGER NULL,                              --@ Vehicle ID from Vehicle table used to carry out the transit trip (foreign key to the Vehicle table)
  "mode" INTEGER NOT NULL DEFAULT 0,                   --@ Transit route type (TODO: Rename to route_type)
  "Est_Departure_Time" INTEGER NOT NULL DEFAULT 0,     --@ Estimated departure time of transit vehicle trip by GTFS in seconds (units: seconds)
  "Act_Departure_Time" INTEGER NOT NULL DEFAULT 0,     --@ Same as above when buses not running in traffic, otherwise experienced based on congestion (units: seconds)
  "Est_Arrival_Time" INTEGER NOT NULL DEFAULT 0,       --@ Estimated arrival time of transit vehicle trip at destination by GTFS in seconds (units: seconds)
  "Act_Arrival_Time" INTEGER NOT NULL DEFAULT 0,       --@ Same as above when buses not running in traffic, otherwise experienced based on congestion (units: seconds)
  "Est_Travel_Time" INTEGER NOT NULL DEFAULT 0,        --@ Estimated travel time in completing the trip in seconds (units: seconds)
  "Act_Travel_Time" INTEGER NOT NULL DEFAULT 0,        --@ Same as above when buses not running in traffic, otherwise experienced based on congestion (units: seconds)
  "Seated_Capacity" INTEGER NOT NULL DEFAULT 0,        --@ Number of travelers that can be seated in the transit vehicle for this trip
  "Standing_Capacity" INTEGER NOT NULL DEFAULT 0,      --@ Number of travelers that can be accommodated standing in the transit vehicle for this trip

  CONSTRAINT "vehicle_fk"
    FOREIGN KEY ("vehicle")
    REFERENCES "Vehicle" ("vehicle_id")
    DEFERRABLE INITIALLY DEFERRED)