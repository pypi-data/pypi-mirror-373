-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Records the households synthesized in the simulation and all associated characteristics and metrics aggregated at the household level.
--@ Certain columns are directly obtained from the ACS, while others are synthesized through demand models executed during simulation.
--@
--@ Records are either a result of population synthesis or are being moved from one Demand database to the next 
--@ when reading population from database.

CREATE TABLE "Household" (
  "household" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ The unique identifier for the household
  "hhold" INTEGER NOT NULL,                               --@ The upstream (i.e. PUMS) identifier for the household
  "location" INTEGER NOT NULL,                            --@ The location to which this household is attached (foreign key to the Location table)
  "persons" INTEGER NOT NULL DEFAULT 0,                   --@ Number of household members
  "workers" INTEGER NOT NULL DEFAULT 0,                   --@ Number of workers in the household as defined by WiF from the ACS (number of people over 15 that worked one week or more in the last year, capped at 3+)
  "vehicles" INTEGER NOT NULL DEFAULT 0,                  --@ Number of vehicles in the household
  "type" INTEGER NOT NULL DEFAULT 0,                      --@ Household type as defined by the ACS and represented the !HHTYPE! enum
  "income" INTEGER NOT NULL DEFAULT 0,                    --@ Annual household income (ACS field HINCP)
  "bikes" INTEGER NOT NULL DEFAULT 0,                     --@ Number of bicycles in the household
  "housing_unit_type" INTEGER NOT NULL DEFAULT 0,         --@ Type of the housing unit !HU_TYPE!
  "ecom" INTEGER NOT NULL DEFAULT 0,                      --@ Number of e-commerce packages received in the simulated day by the household
  "delRat" REAL NULL DEFAULT 0,                           --@ Delivery ratio
  "dispose_veh" INTEGER NOT NULL,                         --@ boolean flag - were one or more vehicles disposed within the household?
  "time_in_home" REAL NOT NULL DEFAULT 0,                 --@ Time this household has been resident at this location (unit: years)
  "Has_Residential_Charging" INTEGER NOT NULL DEFAULT 0,  --@ boolean flag - does household have an EV charging station?
  "num_groceries" INTEGER NOT NULL DEFAULT 0,             --@ Number of grocery deliveries received in the simulated day by the household
  "num_meals" INTEGER NOT NULL DEFAULT 0                  --@ Number of meal deliveries received in the simulation day by the household
  )
