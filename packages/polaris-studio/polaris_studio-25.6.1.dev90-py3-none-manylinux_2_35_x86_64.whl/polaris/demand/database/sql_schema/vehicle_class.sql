-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table defines the various classes of vehicles which can exist within a POLARIS simulation.
--@ It defines physical characteristics of the vehicles such as their size, acceleration and braking.
--@ 

CREATE TABLE "Vehicle_Class" (
  "class_id" INTEGER NOT NULL PRIMARY KEY,  --@ The unique identifier of this class 
  "class_type" TEXT NOT NULL DEFAULT '',    --@ A text based description (human friendly)
  "capacity" INTEGER NOT NULL DEFAULT 0,    --@ Vehicle carrying capacity - not used by POLARIS
  "length" REAL NULL DEFAULT 0,             --@ Length of a typical vehicle (units: meters)
  "max_speed" REAL NULL DEFAULT 0,          --@ Maximum speed of vehicles of this class (units: m/s)
  "max_accel" REAL NULL DEFAULT 0,          --@ Maximum acceleration of vehicles of this class (units: m/s^2)
  "max_decel" REAL NULL DEFAULT 0,          --@ Maximum braking capacity of vehicles of this class (units: m/s^2)
  "ev_ml_class" INTEGER NOT NULL DEFAULT 0  --@ The corresponding class ID within the Tensorflow model for battery consumption (Wh/mile)
)