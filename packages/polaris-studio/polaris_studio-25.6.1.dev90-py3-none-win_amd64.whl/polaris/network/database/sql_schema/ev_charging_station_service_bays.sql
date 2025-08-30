-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all service/maintenace bays available at stations (currently referred to as charging stations) in the model, including all the fields required by Polaris.
--@ Currently used only by TNC/SAV vehicles that are simulated, if specified. 
--@
--@ Not required by all models.
--@ 
--@ SQL script to get a quick run going when there are stations that exist in the data model:
--@ 
--@ INSERT INTO EV_Charging_Station_Service_Bays SELECT ID, 1 FROM EV_Charging_Stations;

CREATE TABLE IF NOT EXISTS EV_Charging_Station_Service_Bays(
    Station_ID INTEGER NOT NULL,         --@ Foreign key reference to an electric vehicle charging station found in the EV_Charging_Stations table
    service_bay_count INTEGER DEFAULT 1, --@ Number of service/maintenance bays available at the electric vehicle charging station 

    FOREIGN KEY (Station_ID) REFERENCES EV_Charging_Stations(ID) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);