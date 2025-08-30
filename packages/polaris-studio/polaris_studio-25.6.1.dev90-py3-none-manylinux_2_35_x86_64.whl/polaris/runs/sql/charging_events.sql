-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DROP TABLE IF EXISTS ev_charging_final_home;
CREATE TABLE ev_charging_final_home AS
SELECT Station_ID, "Location", vehicle, person, Input_Power, Time_In, Time_Start, Time_Out,
       Energy_In_Wh, Energy_Out_Wh, Charging_Fleet_Type, Charging_Station_Type, Has_Residential_Charging,
       Is_Negative_Battery
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY vehicle ORDER BY Time_Out DESC) AS rn
    FROM EV_Charging
    WHERE Charging_Station_Type = 'home'
      AND Charging_Fleet_Type = 'personal'
) sub
WHERE rn = 1;

DROP TABLE IF EXISTS ev_charge_summary;
CREATE TABLE ev_charge_summary AS
SELECT
       "Charging_Station_Type",
       "Charging_Fleet_Type",
       xx_pop_scaling_factor_xx * sum("Energy_Out_Wh"- "Energy_In_Wh")/1000000.0 AS total_energy_charged_MWh,
       xx_pop_scaling_factor_xx * sum(Time_Start - Time_In)/3600.0 AS total_wait_hours,
       xx_pop_scaling_factor_xx * sum(Time_Out - Time_Start)/3600.0 AS total_charge_hours,
       xx_pop_scaling_factor_xx * sum(charged_money) AS total_charged_dollars,
       xx_pop_scaling_factor_xx * sum(CASE WHEN "Energy_Out_Wh"- "Energy_In_Wh">0 THEN 1 ELSE 0 END) AS positive_charge_count,
       xx_pop_scaling_factor_xx * count(*) AS charge_count,
       sum("Energy_Out_Wh"- "Energy_In_Wh")/1000.0/sum(CASE WHEN "Energy_Out_Wh"- "Energy_In_Wh">0 THEN 1 ELSE 0 END) AS average_energy_charged_kWh,
       sum(Time_Start - Time_In)/60.0/count(*) AS average_wait_minutes,
       sum(Time_Out - Time_Start)/60.0/sum(CASE WHEN "Energy_Out_Wh"- "Energy_In_Wh">0 THEN 1 ELSE 0 END) AS average_charge_minutes,
       sum(charged_money)/sum(CASE WHEN "Energy_Out_Wh"- "Energy_In_Wh">0 THEN 1 ELSE 0 END) AS average_paid_dollars_per_event,
       sum(charged_money)*1000.0/sum("Energy_Out_Wh"- "Energy_In_Wh") AS averaged_paid_dollars_per_kWh
FROM "EV_Charging"
GROUP BY 1,2;

-- Has residential charging: -1 for non-household vehicles, 0 for household no chargers, 1 for household with chargers
DROP TABLE IF EXISTS ev_charge_vehicles;
CREATE TABLE ev_charge_vehicles AS
SELECT
    c.class_type AS Vehicle_Class,
    f.type AS Fuel_Type,
    p.type AS Powertrain_Type,
    a.type AS Automation_Type,
    CASE
        WHEN x.hhold < 0 THEN -1
        ELSE h.has_residential_charging
    END AS Has_Residential_Charging,
    xx_pop_scaling_factor_xx * COUNT(*) AS Count
FROM Vehicle_Type v
JOIN fuel_type f        ON v.fuel_type = f.type_id
JOIN powertrain_type p  ON v.powertrain_type = p.type_id
JOIN automation_type a  ON v.automation_type = a.type_id
JOIN vehicle_class c    ON v.vehicle_class = c.class_id
JOIN vehicle x          ON x.type = v.type_id
LEFT JOIN household h   ON x.hhold = h.household
GROUP BY 1,2,3,4,5;

DROP TABLE IF EXISTS ev_charge_trajectory;
CREATE TABLE ev_charge_trajectory AS
SELECT
    x.vehicle_id as vehicle,
    t.trip_id AS trip_id,
    a.person AS person,
    a.seq_num AS seq_num,
    ev.veh_ess_energy AS battery_size,
    t.start/60 AS dept_time,
    t.end/60 AS arr_time,
    l1.zone AS orig_zone,
    l2.zone AS dest_zone,
    t.travel_distance/1609.3 AS distance_mile,
    t.initial_energy_level AS initial_charge,
    t.final_energy_level AS final_charge,
    a.type AS activity_type,
    h.has_residential_charging AS has_charger_at_home
FROM activity a
JOIN trip t         ON a.trip = t.trip_id
JOIN vehicle x      ON x.vehicle_id = t.vehicle
JOIN household h    ON x.hhold = h.household
JOIN Vehicle_Type v ON x.type = v.type_id
JOIN fuel_type f    ON v.fuel_type = f.type_id
JOIN ev_features ev ON v.ev_features_id = ev.ev_features_id
JOIN a.location l1  ON t.origin = l1.location
JOIN a.location l2  ON t.destination = l2.location
WHERE t.mode = 0 AND f.type = 'Elec'
ORDER BY x.vehicle_id, t.start;

DROP TABLE IF EXISTS ev_charge_trajectory_freight;
CREATE TABLE ev_charge_trajectory_freight AS
SELECT
    x.vehicle_id AS vehicle,
    t.trip_id AS trip_id,
    ev.veh_ess_energy AS battery_size,
    t.start/60 AS dept_time,
    t.end/60 AS arr_time,
    l1.zone AS orig_zone,
    l2.zone AS dest_zone,
    t.travel_distance/1609.3 AS distance_mile,
    t.initial_energy_level AS initial_charge,
    t.final_energy_level AS final_charge,
    t.mode
FROM trip t
JOIN vehicle x      ON t.vehicle = x.vehicle_id
JOIN Vehicle_Type v ON x.type = v.type_id
JOIN fuel_type f    ON v.fuel_type = f.type_id
JOIN ev_features ev ON v.ev_features_id = ev.ev_features_id
JOIN a.location l1  ON t.origin = l1.location
JOIN a.location l2  ON t.destination = l2.location
WHERE t.mode in (17, 18, 19, 20) AND f.type = 'Elec'
ORDER BY x.vehicle_id, t.start;

DROP TABLE IF EXISTS ev_charge_trajectory_init;
CREATE TABLE ev_charge_trajectory_init(
  has_charger_at_home INT,
  vehicle INT PRIMARY KEY,
  day_begin,
  initial_charge REAL,
  battery_size REAL,
  SoC
);

DROP TABLE IF EXISTS ev_charge_trajectory_final;
CREATE TABLE ev_charge_trajectory_final(
  has_charger_at_home INT,
  vehicle INT PRIMARY KEY,
  day_end,
  final_charge REAL,
  final_charge2,
  battery_size REAL,
  SoC
);


INSERT INTO ev_charge_trajectory_init
SELECT "has_charger_at_home", "vehicle", min("dept_time") AS day_begin, "initial_charge", "battery_size", "initial_charge"/"battery_size" AS SoC
FROM "ev_charge_trajectory"
GROUP BY vehicle;


-- TODO: This query only has a single agg field... sqlite doesn't guarantee that other fields are from the same row
--       AS the agg field, we need to fix this to ensure we get the right values by using a row_number sub-query
INSERT INTO ev_charge_trajectory_final
SELECT "has_charger_at_home", "vehicle", max("arr_time") AS day_end, "final_charge", 0.0 AS final_charge2, "battery_size", "final_charge"/"battery_size" AS SoC
FROM "ev_charge_trajectory"
GROUP BY vehicle;

update ev_charge_trajectory_final
SET final_charge2 = (select Energy_Out_Wh from EV_Charging_final_home e WHERE e.vehicle = ev_charge_trajectory_final.vehicle)
WHERE exists (select * from EV_Charging_final_home e WHERE e.vehicle = ev_charge_trajectory_final.vehicle);

UPDATE ev_charge_trajectory_final
SET final_charge = final_charge2
WHERE final_charge2 > final_charge;

UPDATE ev_charge_trajectory_final
SET SoC = "final_charge"/"battery_size";

DROP TABLE IF EXISTS ev_charging_events;
CREATE TABLE ev_charging_events AS
SELECT
    c.Charging_Station_Type,
    t.vehicle AS vehicle,
    t.battery_size AS battery_size,
    t.dept_time AS dept_time,
    t.arr_time AS arr_time,
    t.orig_zone AS orig_zone,
    t.dest_zone AS dest_zone,
    t.distance_mile AS distance_mile,
    t.initial_charge AS initial_charge,
    c.Energy_Out_Wh AS station_charge,
    t.activity_type AS activity_type,
    t.has_charger_at_home AS has_charger_at_home
FROM
    ev_charge_trajectory t,
    EV_Charging c
WHERE
    t.vehicle = c.vehicle AND
    t.final_charge = c.Energy_In_Wh AND
    c.Energy_In_Wh < c.Energy_Out_Wh AND
    t.activity_type = 'EV_CHARGING' AND
    Charging_Fleet_Type = 'personal'
ORDER BY t.vehicle, t.dept_time;

DROP TABLE IF EXISTS ev_charge_consumption;
CREATE TABLE ev_charge_consumption AS
SELECT xx_traj_scaling_factor_xx * sum("initial_charge"- "final_charge")/1000000 AS Consumption_MWh
FROM "ev_charge_trajectory";

DROP TABLE IF EXISTS ev_charge_consumption_by_res_charging;
CREATE TABLE ev_charge_consumption_by_res_charging AS
SELECT has_charger_at_home, xx_traj_scaling_factor_xx*sum("initial_charge"- "final_charge")/1000000 AS Consumption_MWh
FROM "ev_charge_trajectory"
GROUP BY has_charger_at_home;

DROP TABLE IF EXISTS ev_charge_summary_stations;
CREATE TABLE ev_charge_summary_stations AS
SELECT
    s.station_type,
    sum(CASE WHEN p.plug_type = 1 THEN p.plug_count else 0 end) AS type_1_plugs,
    sum(CASE WHEN p.plug_type = 2 THEN p.plug_count else 0 end) AS type_2_plugs,
    sum(CASE WHEN p.plug_type = 3 THEN p.plug_count else 0 end) AS type_3_plugs,
    count(distinct p.station_id) AS stations
FROM
    "a"."EV_Charging_Station_Plugs" AS p,
    "a"."EV_Charging_Stations" AS s
WHERE
    p.station_id = s.id
GROUP BY
    s.station_type;