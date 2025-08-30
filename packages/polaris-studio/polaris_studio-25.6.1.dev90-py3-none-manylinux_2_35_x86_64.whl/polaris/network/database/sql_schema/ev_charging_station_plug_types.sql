-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all types of plugs found in electric vehicle charging stations in the model,
--@ including all the fields required by Polaris.
--@ Chargers with power level of 1,000 correspond to Level 1 chargers.
--@ Chargers with power level of 7,000 correspond to Level 2 chargers.
--@ Chargers with power level of 50,000 correspond to dcfc chargers.
--@ Required by all models presently, but will soon be more flexible.

CREATE TABLE IF NOT EXISTS EV_Charging_Station_Plug_Types(
    plug_type_id INTEGER NOT NULL PRIMARY KEY,  --@ Unique identifier for the plug type
    power_level  REAL,                          --@ plug power level (in watts)
    power_source TEXT    NOT NULL               --@ text description of source of energy, defaults to 'Electric'
);

insert into EV_Charging_Station_Plug_Types(plug_type_id,power_level,power_source) values (1,1000,'Electric');
insert into EV_Charging_Station_Plug_Types(plug_type_id,power_level,power_source) values (2,7000,'Electric');
insert into EV_Charging_Station_Plug_Types(plug_type_id,power_level,power_source) values (3,50000,'Electric');