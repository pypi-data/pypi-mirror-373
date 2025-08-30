-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Dictionary of all modes supported for simulation within POLARIS.
--@
--@ This table is currently only used for providing a text based representation of the hard-coded modes
--@ defined in POLARIS (Vehicle_Type_Keys enum).

CREATE TABLE "Mode" (
  "mode_id" INTEGER NOT NULL PRIMARY KEY, --@ Unique identifier for mode !Vehicle_Type_Keys!
  "mode_description" TEXT NOT NULL)       --@ Text input describing the mode