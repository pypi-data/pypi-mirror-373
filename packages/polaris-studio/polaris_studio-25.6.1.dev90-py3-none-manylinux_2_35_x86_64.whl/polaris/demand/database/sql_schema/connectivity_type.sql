-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table holds information about whether a vehicle is a connected vehicle.
--@ Only two options are currently allowed: Yes and No. Other levels of connectivity
--@ can be included as needed.
--@
--@ Static table. POLARIS does not change the value of this table.

CREATE TABLE "Connectivity_Type" (
  "type_id" INTEGER NOT NULL PRIMARY KEY, --@ Identifier for connectivity type
  "type" TEXT NOT NULL DEFAULT '')        --@ Text description of connectivity type: currently Yes or No