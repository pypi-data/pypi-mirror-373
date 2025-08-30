-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
-- ;

-- There must be records in the Firm table for freight model run
SELECT count(*) == 0 FROM Firm;

-- There must be records in the Establishment table for freight model run
SELECT count(*) == 0 FROM Establishment;

-- There must be records in the NAICS_Landuses table for freight model run
SELECT count(*) == 0 FROM Naics_Landuses;

-- There must be records in the Trade_Flow table for freight model run
SELECT count(*) == 0 FROM Trade_Flow;

-- There must be records in the Airport table for freight model run
SELECT count(*) == 0 FROM Airport;

-- There must be records in the Airport_Locations table for freight model run
SELECT count(*) == 0 FROM Airport_Locations;

-- There must be records in the County_Skims table for freight model run
SELECT count(*) == 0 FROM County_Skims;

-- A trade type must be a valid type only 
SELECT COUNT(*) FROM Trade_Flow WHERE trade_type NOT BETWEEN 1 AND 5;

-- A commodity type must be a valid type
SELECT COUNT(*) FROM Trade_Flow WHERE commodity NOT BETWEEN 1 AND 15;

-- An establishment must have employees
SELECT COUNT(*) FROM Establishment WHERE employees < 1;

-- A supplier in the Trade_Flow table must exist in either the Establishment table or the International_port table
SELECT 1
FROM Trade_Flow
WHERE supplier NOT IN (SELECT DISTINCT establishment FROM Establishment 
                       UNION 
                       SELECT DISTINCT international_port from International_port);

-- A receiver in the Trade_Flow table must exist in either the Establishment table or the International_ports table
SELECT 1
FROM Trade_Flow
WHERE receiver NOT IN (SELECT DISTINCT establishment FROM Establishment 
                       UNION 
                       SELECT DISTINCT international_port from International_port);

   
-- A NAICS in the Establishment table must exist in the Naics-Landuses table
SELECT 1 
FROM Establishment
WHERE naics NOT IN (SELECT DISTINCT naics FROM Naics_Landuses);

-- For exports: a supplier must be an establishment and a receiver must an international port
SELECT 1 
FROM Trade_Flow 
WHERE (supplier > 800000000 OR receiver < 800000000) 
AND trade_type = 4;

-- For imports: a supplier must be an international port and a receiver must be an establishment
SELECT 1 
FROM Trade_Flow 
WHERE (supplier < 800000000 OR receiver > 800000000) 
AND trade_type = 5;

-- Check that all intra-country values are present
SELECT county_dest
FROM (
    SELECT DISTINCT county_dest FROM County_Skims
) AS d
WHERE NOT EXISTS (
    SELECT 1
    FROM County_Skims AS s
    WHERE s.county_orig = d.county_dest AND s.county_dest = d.county_dest
);

-- There must be records in the International_Port table for freight model run
SELECT count(*) == 0 FROM International_Port;

-- There must be records in the Rail_Operator table for freight model run
SELECT count(*) == 0 FROM Rail_Operator;

-- There must be records in the Rail_Operator_Counties table for freight model run
SELECT count(*) == 0 FROM Rail_Operator_Counties;

-- There must be records in the Rail_Operator_Railports table for freight model run
SELECT count(*) == 0 FROM Rail_Operator_Railports;

-- There must be records in the Railport table for freight model run
SELECT count(*) == 0 FROM Railport;

-- There must be records in the Truck_Poe table for freight model run
SELECT count(*) == 0 FROM Truck_Poe;