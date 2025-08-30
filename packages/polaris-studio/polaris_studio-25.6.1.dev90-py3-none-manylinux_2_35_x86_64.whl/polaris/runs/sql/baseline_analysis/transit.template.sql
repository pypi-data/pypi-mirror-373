-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
-- FROM HERE ODWN

DROP TABLE IF EXISTS boardings_by_agency_mode;
CREATE TABLE boardings_by_agency_mode as
SELECT
    ta.agency as agency,
    transit_mode_fn as "mode",
    scaling_factor*sum(tvl.value_boardings) as boardings,
    scaling_factor*sum(tvl.value_alightings) as alightings
FROM
    "Transit_Vehicle_links" tvl,
    transit_vehicle tv,
    a.transit_trips tt,
    a.transit_patterns tp,
    a.transit_routes tr,
    a.transit_agencies ta
where
    tvl.value_transit_vehicle_trip = tv.transit_vehicle_trip and
    tvl.value_transit_vehicle_trip = tt.trip_id and
    tp.pattern_id = tt.pattern_id and
    tr.route_id = tp.route_id AND
    tr.agency_id = ta.agency_id
group by 1,2
order by 1,2
;


DROP TABLE IF EXISTS boardings_by_agency_mode_time;
CREATE TABLE boardings_by_agency_mode_time as
SELECT
    ta.agency as agency,
    transit_mode_fn as "mode",
    cast(cast(cast(tvl.value_act_departure_time as real)/1800 as int) as real)/2 as HH,
    scaling_factor*sum(tvl.value_boardings) as boardings,
    scaling_factor*sum(tvl.value_alightings) as alightings
FROM
    "Transit_Vehicle_links" tvl,
    transit_vehicle tv,
    a.transit_trips tt,
    a.transit_patterns tp,
    a.transit_routes tr,
    a.transit_agencies ta
where
    tvl.value_transit_vehicle_trip = tv.transit_vehicle_trip and
    tvl.value_transit_vehicle_trip = tt.trip_id and
    tp.pattern_id = tt.pattern_id and
    tr.route_id = tp.route_id AND
    tr.agency_id = ta.agency_id
group by agency, mode, HH
order by agency, mode desc, HH ;

DROP TABLE IF EXISTS boardings_by_agency_mode_route_time;
CREATE TABLE boardings_by_agency_mode_route_time as
SELECT
    ta.agency as agency,
    transit_mode_fn as "mode",
    tr.route as route,
    cast(cast(cast(tvl.value_act_departure_time as real)/1800 as int) as real)/2 as HH,
    scaling_factor*sum(tvl.value_boardings) as boardings,
    scaling_factor*sum(tvl.value_alightings) as alightings
FROM
    "Transit_Vehicle_links" tvl,
    transit_vehicle tv,
    a.transit_trips tt,
    a.transit_patterns tp,
    a.transit_routes tr,
    a.transit_agencies ta
where
    tvl.value_transit_vehicle_trip = tv.transit_vehicle_trip and
    tvl.value_transit_vehicle_trip = tt.trip_id and
    tp.pattern_id = tt.pattern_id and
    tr.route_id = tp.route_id AND
    tr.agency_id = ta.agency_id
group by agency, mode, route, HH
order by agency, mode desc, route, HH ;

DROP TABLE IF EXISTS boardings_by_agency_mode_route_stop_time;
CREATE TABLE boardings_by_agency_mode_route_stop_time as
SELECT
    ta.agency as agency,
    transit_mode_fn as "mode",
    tr.route as route,
    ts.stop as stop,
    cast(cast(cast(tvl.value_act_departure_time as real)/1800 as int) as real)/2 as HH,
    scaling_factor*sum(tvl.value_boardings) as boardings
FROM
    "Transit_Vehicle_links" tvl,
    transit_vehicle tv,
    a.transit_trips tt,
    a.transit_patterns tp,
    a.transit_routes tr,
    a.transit_agencies ta,
    a.transit_links tl,
    a.transit_stops ts
where
    tvl.value_transit_vehicle_trip = tv.transit_vehicle_trip and
    tvl.value_transit_vehicle_trip = tt.trip_id and
    tp.pattern_id = tt.pattern_id and
    tr.route_id = tp.route_id AND
    tr.agency_id = ta.agency_id and
    tl.transit_link = tvl.value_link AND
    tl.from_node = ts.stop_id AND
    tl.type < 3
group by agency, mode, route, stop, HH
order by agency, mode desc, route, stop, HH ;


DROP TABLE IF EXISTS boardings_by_agency_mode_area_type;
CREATE TABLE boardings_by_agency_mode_area_type as
SELECT
    ta.agency as agency,
    tv.mode as mode,
    z.area_type as area_type,
    scaling_factor*sum(tvl.value_boardings) as boardings,
    scaling_factor*sum(tvl.value_alightings) as alightings
FROM
    "Transit_Vehicle_links" tvl,
    transit_vehicle tv,
    a.transit_trips tt,
    a.transit_patterns tp,
    a.transit_routes tr,
    a.transit_agencies ta,
    a.transit_stops ts,
    a.transit_links tl,
    a.zone z
where
    tvl.value_transit_vehicle_trip = tv.transit_vehicle_trip and
    tvl.value_transit_vehicle_trip = tt.trip_id and
    tp.pattern_id = tt.pattern_id and
    tr.route_id = tp.route_id and
    ta.agency_id = tr.agency_id AND
    tl.transit_link = tvl.value_link and
    ts.stop_id = tl.from_node and
    ts.zone = z.zone
group by
    ta.agency,
    tv.mode,
    z.area_type
order by
    ta.agency,
    tv.mode desc,
    z.area_type
;

DROP TABLE IF EXISTS transit_vmt_pmt_occ;
CREATE TABLE transit_vmt_pmt_occ as
SELECT
    a.agency as agency,
    transit_mode_fn as "mode",
    sum(value_length)/1609.34 as VMT,
    scaling_factor*sum((value_seated_load + value_standing_load)*value_length)/1609.34 as PMT,
    scaling_factor*sum((value_seated_load + value_standing_load)*value_length)/sum(value_length) as Occupancy
FROM
    "Transit_Vehicle_links" l,
    a.transit_trips t,
    a.transit_patterns p,
    a.transit_routes tr,
    a.transit_agencies a
where
    l.value_transit_vehicle_trip = t.trip_id
    and t.pattern_id = p.pattern_id
    and p.route_id = tr.route_id
    and tr.agency_id = a.agency_id
group by 
    agency, mode ;

DROP TABLE IF EXISTS transit_vmt_pmt_occ_by_period;
CREATE TABLE transit_vmt_pmt_occ_by_period as
SELECT
    ((l.value_act_arrival_time >= 6*3600.0 and l.value_act_arrival_time < 9*3600.0)
    or (l.value_act_arrival_time >= 15*3600.0 and l.value_act_arrival_time < 18*3600.0)) as peak_period,
    a.agency as agency,
    transit_mode_fn as "mode",
    sum(value_length)/1609.34 as VMT,
    scaling_factor*sum((value_seated_load + value_standing_load)*value_length)/1609.34 as PMT,
    scaling_factor*sum((value_seated_load + value_standing_load)*value_length)/sum(value_length) as Occupancy
FROM "Transit_Vehicle_links" l,
     a.transit_trips t,
     a.transit_patterns p,
     a.transit_routes tr,
     a.transit_agencies a
where l.value_transit_vehicle_trip = t.trip_id
  and t.pattern_id = p.pattern_id
  and p.route_id = tr.route_id
  and tr.agency_id = a.agency_id
group by peak_period, agency, mode ;

-- DROP TABLE IF EXISTS avg_wait_and_total_time;
-- CREATE TABLE avg_wait_and_total_time as
-- select
--     avg(act_bus_wait_time + act_rail_wait_time + act_comm_rail_wait_time)/60 as avg_wait_time,
--     avg(act_bus_ivtt + act_rail_ivtt + act_comm_rail_ivtt)/60 as avg_ivtt,
--     avg(act_duration - (act_bus_wait_time + act_rail_wait_time + act_comm_rail_wait_time + act_bus_ivtt + act_rail_ivtt + act_comm_rail_ivtt))/60 as avg_ovtt,
--     avg(act_duration)/60 as avg_duration,
--     avg(est_wait_count + est_tnc_wait_count)-1 as avg_transfer_count
-- from
--     path_multimodal
-- where
--     act_bus_wait_time + act_rail_wait_time + act_comm_rail_wait_time > 0;

-- DROP TABLE IF EXISTS avg_wait_and_total_time_by_income;
-- CREATE TABLE avg_wait_and_total_time_by_income as
-- select
--     income_quintile_fn as INCOME_QUINTILE,
--     avg(act_bus_wait_time + act_rail_wait_time + act_comm_rail_wait_time)/60 as avg_wait_time,
--     avg(act_bus_ivtt + act_rail_ivtt + act_comm_rail_ivtt)/60 as avg_ivtt,
--     avg(act_bike_time+act_walk_time+act_car_time)/60 as avg_ovtt,
--     avg(act_duration)/60 as avg_duration,
--     avg(act_wait_count)-1 as avg_transfer_count
-- from path_multimodal p, activity, person, trip, household
--     where act_bus_wait_time + act_rail_wait_time + act_comm_rail_wait_time > 0
--     and p.id = trip.path_multimodal and
--     activity.trip = trip.trip_id and
--     activity.person = person.person and
--     person.household = household.household
-- GROUP BY
--     INCOME_QUINTILE;

-- DROP TABLE IF EXISTS avg_wait_and_total_time_TNC;
-- CREATE TABLE avg_wait_and_total_time_TNC as
-- select
--     avg(act_bus_wait_time + act_rail_wait_time + act_comm_rail_wait_time)/60 as avg_wait_time,
--     avg(act_duration - (act_bus_wait_time + act_rail_wait_time + act_comm_rail_wait_time + act_bus_ivtt + act_rail_ivtt + act_comm_rail_ivtt + act_bike_time + act_walk_time))/60 as avg_TNC_Time,
--     avg(act_bus_ivtt + act_rail_ivtt + act_comm_rail_ivtt)/60 as avg_ivtt,
--     avg(act_bike_time + act_walk_time)/60 as avg_active_ovtt,
--     avg(act_duration)/60 as avg_duration,
--     avg(act_wait_count)-1 as avg_transfer_count
-- from
--     path_multimodal
-- where
--     act_bus_wait_time + act_rail_wait_time + act_comm_rail_wait_time > 0
--     and mode = 15;