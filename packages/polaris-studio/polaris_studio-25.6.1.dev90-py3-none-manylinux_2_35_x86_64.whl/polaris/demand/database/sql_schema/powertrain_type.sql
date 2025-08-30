-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Table denoting the different powertrain types available in POLARIS.
--@ Primarily used for descrbing vehicle characteristics when used along with Autonomie.

--@ Static table. Table is not modified by POLARIS

CREATE TABLE "Powertrain_Type" (
  "type_id" INTEGER NOT NULL PRIMARY KEY, --@ Unique identifier for the powertrain type
  "type" TEXT NOT NULL DEFAULT ''         --@ Text description of the powertrain !Powertrain_Type_Keys!
)