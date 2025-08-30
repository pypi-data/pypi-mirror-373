-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Provides ability to vary electricity costs by flexible time periods for each utility. 
--@ It is linked to the Electricity_Provider table through a fk on station_id.
--@ unit_price is the cost per kWh for certain types of pricing, and cost overall for others expressed in dollars
--@
--@ Not required by all models and is okay to be empty.

CREATE TABLE IF NOT EXISTS Electricity_Provider_Pricing(
    id INTEGER NOT NULL PRIMARY KEY, --@ Primary key referencing the pricing strategy used
    Provider_ID INTEGER NOT NULL,    --@ Foreign key to electricity provider who is enforcing pricing strategy
    "type" TEXT NOT NULL,            --@ Type of pricing strategy enforced. Can be one of  THE ENUM IS THIS< BUT IT IS NOT WORKING @Electricity_Pricing_Type@
    start_seconds INTEGER NOT NULL,  --@ Simulation time (in seconds) that the pricing strategy starts being enforced
    end_seconds INTEGER NOT NULL,    --@ Simulation time (in seconds) that the pricing strategy stops being enforced
    unit_price REAL NOT NULL,        --@ Cost (in $)  as applied by the type suggested above

    CONSTRAINT "fk_prov_id" FOREIGN KEY("Provider_ID") REFERENCES Electricity_Provider("Provider_ID") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);

