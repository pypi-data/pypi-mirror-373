-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Firms table have the attributes of the firm:  
--@ employment, sector, number of memeber establishments, revenue, 
--@ distribution center areas
--@

CREATE TABLE Firm (
    "firm"                  INTEGER NOT NULL PRIMARY KEY, --@ The unique identifier of this firm
    "naics"                 INTEGER NOT NULL DEFAULT 0,   --@ The 3-digit NAICS code of the firm
    "total_establishments"  INTEGER NOT NULL DEFAULT 0,   --@ Total number of member establishments of the firm
    "total_employees"       INTEGER NOT NULL DEFAULT 0,   --@ Total number of employees of the firm
    "dc_total_area"         REAL             DEFAULT 0,   --@ Total area of the distribution centers (units: square meters)
    "revenue"               REAL             DEFAULT 0    --@ The revenue of the firm (units: $USD millions)
);
