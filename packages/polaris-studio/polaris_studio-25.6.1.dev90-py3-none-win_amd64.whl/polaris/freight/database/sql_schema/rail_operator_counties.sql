-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ List of rail operators by county in the model
--@

CREATE TABLE Rail_Operator_Counties (
    "rail_operator" INTEGER NOT NULL DEFAULT 0,  --@ The unique identifier of the rail operator as in the Rail_Operator table
    "county"        INTEGER NOT NULL DEFAULT 0   --@ County FIPS code

);
