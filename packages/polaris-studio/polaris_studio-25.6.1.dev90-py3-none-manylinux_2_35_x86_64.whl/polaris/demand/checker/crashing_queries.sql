-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
-- Comment line is the error message we will insert the error info in

-- Checks in this file are just overall consistency checks, and a network that fails these checks WILL CRASH the run

-- DEMAND CHECKS;

-- There are NON-EV vehicle types with NON-NULL ev_feature_id: [{}]
select type_id from Vehicle_Type where fuel_type!=4 and ev_features_id>0;
