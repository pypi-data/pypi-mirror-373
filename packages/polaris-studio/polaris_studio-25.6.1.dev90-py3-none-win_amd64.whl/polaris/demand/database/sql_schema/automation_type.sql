-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table holds information about the various levels of automation that can exist within 
--@ a given vehicular fleet. Vehicles have a vehicle_type and each vehicle_type has an associated
--@ automation_type (this table) which defines the abilities of that vehicle type in a connected 
--@ and autonomous network.

CREATE TABLE "Automation_Type" (
  "type_id" INTEGER NOT NULL PRIMARY KEY,  --@ The unique identifier for this type of automation
  "type" TEXT NOT NULL DEFAULT '',         --@ Human readable identifier
  "acc" INTEGER NOT NULL,                  --@ boolean flag - does vehicle support adaptive cruise control (ACC)?
  "cacc" INTEGER NOT NULL,                 --@ boolean flag - does vehicle support connected ACC?
  "connected_signal" INTEGER NOT NULL,     --@ boolean flag - does vehicle support communication with connected signals?
  "fully_autonomous" INTEGER NOT NULL      --@ boolean flag - does vehicle support fully autonomous driving mode?
)