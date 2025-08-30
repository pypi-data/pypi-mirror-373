-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The establishments table include endogenous establishments
--@ and a subset of the exogenous establishments and their
--@ attributes: parent firm, sector, county, employees, 
--@ medium duty and heavy duty truck fleets,
--@ production and consumption of freight tonnage
--@

CREATE TABLE Establishment (
    "establishment"         INTEGER NOT NULL  PRIMARY KEY,  --@ The unique identifier of this establishment
    "firm"                  INTEGER NOT NULL,               --@ The parent firm identifier (foreign key to the Firm table)
    "naics"                 INTEGER NOT NULL,               --@ The 3-digit NAICS code of the establishment
    "county"                INTEGER NOT NULL,               --@ The county FIPS code of the establishment 
    "location"              INTEGER           DEFAULT -1,   --@ The selected location of the establishment
    "employees"             INTEGER NOT NULL  DEFAULT 0,    --@ Number of employees
    "medium_duty_trucks"    INTEGER           DEFAULT 0,    --@ Number of medium duty trucks in the firm fleet
    "heavy_duty_trucks"     INTEGER           DEFAULT 0,    --@ Number of heavy duty trucks in the firm fleet
    "production"            REAL              DEFAULT 0,    --@ Freight production (units: metric tons)
    "consumption"           REAL              DEFAULT 0,    --@ Freight consumption (units: metric tons)

    CONSTRAINT firm_fk FOREIGN KEY (firm)
    REFERENCES Firm (firm) DEFERRABLE INITIALLY DEFERRED
);
