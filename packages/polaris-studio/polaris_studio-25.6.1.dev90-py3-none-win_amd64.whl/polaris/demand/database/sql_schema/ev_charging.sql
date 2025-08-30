-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The EV_Charging table holds information of the charging activities that occur
--@ during simulation. Each individual vehicle that charges, either at home or at a charging station,
--@ logs information regarding its charging event here.

CREATE TABLE "EV_Charging" (
  "Station_ID" INTEGER NULL DEFAULT 0,                   --@ Identifier for where the vehicle charged. Refers to a EV_Charging_Station ID, -1 if not a real station (home, depot, dock etc.)
  "Location" INTEGER NULL DEFAULT 0,                     --@ Identifier for the Location ID of where charging is happening from the Supply DB Location table
  "Charging_Fleet_Type" TEXT NOT NULL DEFAULT '',        --@ Text description of whether the charging vehicle is Personal, TNC, or freight
  "Charging_Station_Type" TEXT NOT NULL DEFAULT '',      --@ Text description of whether charging occurs at a public station, a private_tnc station, a public_freight station, home, work, depot, or dock
  "Has_Residential_Charging" INTEGER NOT NULL DEFAULT 0, --@ boolean flag - does the vehicle have access to charging at home
  "vehicle" INTEGER NULL,                                --@ Vehicle that was being charged (foreign key to the Vehicle table)
  "person" INTEGER NULL,                                 --@ Person that charged the vehicle (foreign key to the Person table)  
  "Input_Power" REAL NOT NULL DEFAULT 0,                 --@ Power at which the charging occured (unites: W)
  "Time_In" INTEGER NOT NULL DEFAULT 0,                  --@ Time when the vehicle arrives at a charging station or home to begin charging. (units: seconds)
  "Time_Start" INTEGER NOT NULL DEFAULT 0,               --@ Time when the vehicle actually begins to charge (when electrons start flowing) (units: seconds)
  "Time_Out" INTEGER NOT NULL DEFAULT 0,                 --@ Time when the vehicle leaves the charging station after completing charging, or stops charging at home. (units: seconds)  
  "Energy_In_Wh" REAL NULL DEFAULT 0,                    --@ Vehicle's battery level when it arrives to charge (units: Wh)
  "Energy_Out_Wh" REAL NULL DEFAULT 0,                   --@ Vehicle's battery level when charging is completed (units: Wh)
  "Battery_In" REAL NULL DEFAULT 0,                      --@ Vehicle's SoC when it arrives to charge (ranges from 0.0 to 100.0)
  "Battery_Out" REAL NULL DEFAULT 0,                     --@ Vehicle's SoC when charging is completed (ranges from 0.0 to 100.0)
  "Charged_Money" REAL NULL DEFAULT 0,                   --@ Monetary cost of charging in US Dollars
  "Miles_In" REAL NULL DEFAULT 0,                        --@ For TNC vehicles, value denoting what the available range is when vehicle enters charging station (units: miles)
  "Miles_Out" REAL NULL DEFAULT 0,                       --@ For TNC vehicles, value denoting what the available range is when vehicle exits charging station (units: miles)
  "Is_Negative_Battery" INTEGER NOT NULL DEFAULT 0,       --@ boolean flag - did the vehicle arrive at charging station with a negative battery level (meaning it did not have enough battery to even get to the charging station)
  CONSTRAINT "vehicle_fk"
    FOREIGN KEY ("vehicle")
    REFERENCES "Vehicle" ("vehicle_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "person_fk"
    FOREIGN KEY ("person")
    REFERENCES "Person" ("person")
    DEFERRABLE INITIALLY DEFERRED)