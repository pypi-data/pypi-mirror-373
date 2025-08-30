-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Table denotes the different fleets operating within the simulation.
--@ Can be a TNC fleet, transit fleet, or freight-related fleet.
--@

CREATE TABLE "Fleet" (
  "fleet" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ unique identifier denoting the fleet
  "name" TEXT NOT NULL DEFAULT ''                     --@ text identifying the name of the fleet. Example includes "Operator_1"
)