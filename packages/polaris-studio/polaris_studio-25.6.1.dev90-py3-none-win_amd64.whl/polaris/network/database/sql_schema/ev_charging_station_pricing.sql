-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Provides ability to vary charging costs by hour of day on a per EVCS basis. 
--@ It is linked to the EV_Charging_Stations table through a foreign key on station_id.
--@
--@ Not required by all models and is okay to be empty.

CREATE TABLE IF NOT EXISTS EV_Charging_Station_Pricing(
    station_id INTEGER NOT NULL, --@ Foreign key reference to an electric vehicle charging station found in the EV_Charging_Station table
    time_hour  INTEGER NOT NULL, --@ The hour in the day to express the time-varying cost of charging
    unit_price REAL    NOT NULL, --@ the cost (in dollars) per kWh expressed

    CONSTRAINT "fk_stat_id" FOREIGN KEY("station_id") REFERENCES EV_Charging_Stations("ID") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);

