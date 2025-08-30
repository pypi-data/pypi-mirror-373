-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Vehicle table holds records for all vehicles simulated in POLARIS.
--@ This includes household-owned vehicles as well as fleet-owned vehicles.
--@

CREATE TABLE "Vehicle" (
  "vehicle_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ Unique identifier of this vehicle 
  "hhold" INTEGER NOT NULL DEFAULT 0,                      --@ Household to which this vehicle belongs. Negative values represent that the vehicle is fleet-owned. (foreign key to the Household table)
  "parking" INTEGER NOT NULL DEFAULT 0,                    --@ Not used
  "L3_wtp" INTEGER NOT NULL DEFAULT 0,                     --@ Not used
  "L4_wtp" INTEGER NOT NULL DEFAULT 0,                     --@ Not used
  "type" INTEGER NOT NULL,                                 --@ Vehicle characteristics (foreign key to the Vehicle_Type table)
  "fleet" INTEGER NULL,                                    --@ Fleet the vehicle belongs to, if any
  "subtype" INTEGER NOT NULL DEFAULT 0,                    --@ Not used

  CONSTRAINT "type_fk"
    FOREIGN KEY ("type")
    REFERENCES "Vehicle_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "fleet_fk"
    FOREIGN KEY ("fleet")
    REFERENCES "Fleet" ("fleet")
    DEFERRABLE INITIALLY DEFERRED);