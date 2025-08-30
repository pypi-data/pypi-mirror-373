-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Table representing the different levels of vintage (age) for a vehicle that is currently allowed by POLARIS
--@ Primarily used when passing along vehicle characteristic to Autonomie.
--@
--@ Static table. POLARIS does not modify the outputs.

CREATE TABLE "Vintage_Type" (
  "type_id" INTEGER NOT NULL PRIMARY KEY, --@ Unique identifier of this vintage type
  "type" TEXT NOT NULL DEFAULT '')        --@ Text description of vintage type and currently includes: 0-5 years, 6-10 years, and 10+ years