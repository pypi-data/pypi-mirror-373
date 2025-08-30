-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists number and type of plugs available at each electric vehicle charging station
--@
--@ Not required by all models.

CREATE TABLE IF NOT EXISTS EV_Charging_Station_Plugs(
    station_id INTEGER NOT NULL,  --@ Foreign key reference to the electric vehicle charging station defined in the EV_Charging_Station table
    plug_type  INTEGER NOT NULL,  --@ Foreign key reference to the type of plug as available in the EV_Charging_Station_Plug_Types table
    plug_count INTEGER DEFAULT 0, --@ Number of plugs of specified type found at specified electric vehicle charging station

    CONSTRAINT "fk_stat_id" FOREIGN KEY("station_id") REFERENCES EV_Charging_Stations("ID") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "fk_plug_type" FOREIGN KEY("plug_type") REFERENCES EV_Charging_Station_Plug_Types("plug_type_id") DEFERRABLE INITIALLY DEFERRED
);

