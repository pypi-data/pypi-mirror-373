-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
-- Comment line is the error message we will insert the error info in

-- Checks in this file are just cristal consistency checks, and a demand that fails these checks WILL CRASH the cristal run

-- CRISTAL-DEMAND CHECKS;

-- There are no records in the Firms table for model run
SELECT count(*) == 0 FROM Firms;

-- There are no records in the Establishments table for cristal run
SELECT count(*) == 0 FROM Establishments;