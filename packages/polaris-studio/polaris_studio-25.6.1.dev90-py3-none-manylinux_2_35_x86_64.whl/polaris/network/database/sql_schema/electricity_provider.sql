-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Provides the electric utilities in the region. The associated pricing table provides the type of collection used by utility. 
--@ Useful in understanding cost of electricity (that is not at the wholesale rate)
--@
--@ Not required by all models and is okay to be empty.

CREATE TABLE IF NOT EXISTS Electricity_Provider(
    Provider_ID INTEGER NOT NULL PRIMARY KEY, --@ Primary key for electric utility in the region
    name              TEXT DEFAULT '', --@ Name of the electric utility represented
    fixed_fee_per_kWh REAL DEFAULT 0   --@ Any fixed fees (in $ / kWh) charged by the utility. More complex pricing schemes stored in Electricity_Provider_Pricing
);