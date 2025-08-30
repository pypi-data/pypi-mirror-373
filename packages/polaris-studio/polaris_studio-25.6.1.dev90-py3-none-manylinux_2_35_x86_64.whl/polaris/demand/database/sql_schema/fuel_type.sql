-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Table that denotes the vehicle fuel types supported for vehicles simulated in POLARIS
--@ Primarily used for descrbing vehicle characteristics when used along with Autonomie.
--@
--@ Static table. POLARIS does not modify the table.

CREATE TABLE "Fuel_Type" (
  "type_id" INTEGER NOT NULL PRIMARY KEY, --@ Unique identifier for fuel type
  "type" TEXT NOT NULL DEFAULT ''         --@ Text input for type of fuel !Fuel_Type_Keys!
)