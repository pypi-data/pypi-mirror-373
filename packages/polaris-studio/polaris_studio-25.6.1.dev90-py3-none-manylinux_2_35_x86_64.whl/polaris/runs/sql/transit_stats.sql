-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DROP VIEW IF EXISTS v_transit_trips_by_agency_mode_time;
CREATE VIEW v_transit_trips_by_agency_mode_time as
SELECT ta.agency,
       m.mode_name, 
       (ts.departure / 3600) % 24 as departure_hh_bin,
       count(*) as trip_count
FROM transit_trips_schedule ts,
     transit_trips tt,
     transit_patterns tp,
     transit_routes tr,
     transit_agencies ta, 
     transit_modes m
WHERE ts.trip_id = tt.trip_id and
      ts."index" = 0 and
      tt.pattern_id = tp.pattern_id and
      tp.route_id = tr.route_id AND
      tr.agency_id = ta.agency_id AND
      tr.type = m.mode_id
group by ta.agency, tr."type", departure_hh_bin
order by ta.agency, tr."type" desc, departure_hh_bin;

DROP VIEW IF EXISTS v_transit_trips_by_agency_mode;
CREATE VIEW v_transit_trips_by_agency_mode as
SELECT agency, mode_name, sum(trip_count)
FROM v_transit_trips_by_agency_mode_time
GROUP BY agency, mode_name;

DROP VIEW IF EXISTS v_transit_pattern_stop_counter;
CREATE  VIEW v_transit_pattern_stop_counter as
SELECT
    pattern_id,
    count(*) + 1 as stop_count
FROM
    Transit_pattern_links
GROUP BY
    pattern_id
;

DROP VIEW IF EXISTS v_trip_stop_counter;
CREATE  VIEW v_trip_stop_counter as
select trip_id, count(*) as stop_count from transit_trips_schedule group by trip_id;

DROP VIEW IF EXISTS v_pattern_mapping_stop_counter;
CREATE  VIEW v_pattern_mapping_stop_counter as
select pattern_id, count(*) as stop_count from transit_pattern_mapping where stop_id not null group by pattern_id;

drop view if exists v_transit_pattern_lengths;
create view v_transit_pattern_lengths AS
SELECT pattern_id, sum(length) as length 
from transit_links
group by pattern_id;

DROP VIEW IF EXISTS v_transit_pattern_summary;
CREATE VIEW v_transit_pattern_summary AS 
SELECT
    tp.pattern_id as pattern_id,
    case
        when (ts.departure/3600) + 1 <= 24 then (ts.departure/3600)
        else (ts.departure/3600) - 24 end
    as departure_hh_bin,
    tp.route_id as route_id,
    tr.agency_id as agency_id,
    ta.agency as agency_name,
    tr.type as route_type,
    count(*) as freq,
    coalesce(sum(tt.number_of_cars), 0) as number_of_cars,
    avg(cast(ts2.departure - ts.departure as real)) as avg_triptime_seconds,
    avg(cast(tt.total_capacity as real))  as avg_capacity,
    psc.stop_count as stop_count,
    pl.length as length_meter, 
    2.23694*sum(pl.length)/sum(cast(ts2.departure - ts.departure as real)) as avg_speed_mph -- 2.23 m/s -> mph
FROM
    transit_agencies ta,
    transit_routes tr,
    transit_patterns tp,
    transit_trips tt,
    transit_trips_schedule ts,
    transit_trips_schedule ts2,
    v_transit_pattern_stop_counter as psc,
    v_transit_pattern_lengths pl
WHERE
    ta.agency_id = tr.agency_id and
    tr.route_id = tp.route_id and
    tp.pattern_id = tt.pattern_id and
    tt.trip_id = ts.trip_id and
    tt.trip_id = ts2.trip_id and
    tp.pattern_id = psc.pattern_id and
    ts."index" = 0 and
    ts2."index" = psc.stop_count - 1 AND
    pl.pattern_id = psc.pattern_id
GROUP BY
    tt.pattern_id,
    departure_hh_bin
ORDER BY
    tt.pattern_id,
    departure_hh_bin
;

DROP VIEW IF EXISTS v_transit_operating_cost;
CREATE VIEW v_transit_operating_cost AS
SELECT
    p.agency_name,
    m.mode_name,
    sum(p.length_meter * freq)/1609.34 as VMT,
    sum(p.length_meter * p.number_of_cars)/1609.34 as train_car_miles,
    sum(avg_triptime_seconds * freq / 3600.0) as VHT,
    sum(avg_triptime_seconds * p.number_of_cars / 3600.0) as train_car_hours,
    case
        when p.number_of_cars >= p.freq then sum(m.operating_cost_per_hour * avg_triptime_seconds * p.number_of_cars / 3600)
        else sum(m.operating_cost_per_hour * avg_triptime_seconds * freq / 3600)
    end as operating_cost,
    m.operating_cost_per_hour as unit_cost_per_hour
FROM
    v_transit_pattern_summary p,
    transit_modes m
where
    p.route_type = m.mode_id
group by
    p.agency_name,
    m.mode_name
order by
    p.agency_name,
    m.mode_name
;

DROP VIEW IF EXISTS v_transit_trips_ttime_by_agency_mode_time;
CREATE VIEW v_transit_trips_ttime_by_agency_mode_time as
SELECT
    ta.agency,
    m.mode_name,
    case
        when (ts.departure/3600) + 1 <= 24 then (ts.departure/3600)
        else (ts.departure/3600) - 24 end
    as departure_hh_bin,
    avg(cast(ts2.departure - ts.departure as real))/60 as avg_dur_minute,
    2.23694*sum(pl.length)/sum(cast(ts2.departure - ts.departure as real)) as avg_speed_mph -- 2.23 m/s -> mph
FROM
    transit_modes m,
    transit_trips_schedule ts,
    transit_trips_schedule ts2,
    transit_trips tt,
    transit_patterns tp,
    transit_routes tr,
    transit_agencies ta,
    v_trip_stop_counter tsc,
    v_transit_pattern_lengths pl
WHERE
    ts.trip_id = tt.trip_id and
    ts2.trip_id = tt.trip_id and
    tsc.trip_id = tt.trip_id and
    ts."index" = 0 and
    ts2."index" = tsc.stop_count - 1 and
    tt.pattern_id = tp.pattern_id and
    tp.route_id = tr.route_id AND
    tr.agency_id = ta.agency_id AND
    pl.pattern_id = tp.pattern_id and
    tr."type" = m.mode_id
group by
    ta.agency,
    tr."type",
    departure_hh_bin
order by
    ta.agency,
    tr."type" desc,
    departure_hh_bin;

DROP VIEW IF EXISTS  v_transit_trips_ttime_by_agency_mode;
CREATE VIEW v_transit_trips_ttime_by_agency_mode as
SELECT 
    ta.agency as agency,
    m.mode_name,	
    avg(cast(ts2.departure - ts.departure as real))/60.0 as avg_dur_minute,
    2.23694*sum(pl.length)/sum(cast(ts2.departure - ts.departure as real)) as avg_speed_mph -- 2.23 m/s -> mph
FROM
    transit_modes m,
    transit_trips_schedule ts,
    transit_trips_schedule ts2,
    transit_trips tt, 
    transit_patterns tp, 
    transit_routes tr,
    transit_agencies ta,
    v_trip_stop_counter tsc,
    v_transit_pattern_lengths pl
WHERE
    ts.trip_id = tt.trip_id and
    ts2.trip_id = tt.trip_id and
    tsc.trip_id = tt.trip_id and
    ts."index" = 0 and
    ts2."index" = tsc.stop_count - 1 and
    tt.pattern_id = tp.pattern_id and 
    tp.route_id = tr.route_id AND
    tr.agency_id = ta.agency_id AND
    pl.pattern_id = tp.pattern_id and
    tr."type" = m.mode_id
group by 
    ta.agency,
    tr."type"
order by
    ta.agency,
    tr."type" desc;

DROP VIEW IF EXISTS  v_transit_trips_ttime;
CREATE VIEW v_transit_trips_ttime as
SELECT
    ta.agency as agency,
    m.mode_name,
    tr.route as route,
    tp.pattern_id as pattern_id,
    tt.trip_id as trip_id,
    ts."index" as "index",
    tpl.transit_link as transit_link,
    ts.departure departure_a,
    ts2.departure departure_b,
    tl."length" as length_meter,
    ts2.departure - ts.departure as duration_seconds,
    3.6*tl."length"/(ts2.departure - ts.departure) as speed_kph
FROM
    transit_modes m,
    transit_trips_schedule ts,
    transit_trips_schedule ts2,
    transit_trips tt,
    transit_patterns tp,
    transit_routes tr,
    transit_agencies ta,
    transit_pattern_links tpl,
    transit_links tl
WHERE
    tr.agency_id = ta.agency_id AND
    tp.route_id = tr.route_id AND
    tt.pattern_id = tp.pattern_id and
    ts.trip_id = tt.trip_id and
    ts2.trip_id = ts.trip_id and
    ts."index" + 1 =  ts2."index" and
    tpl."index" = ts."index" and
    tpl.pattern_id = tp.pattern_id AND
    tpl.transit_link = tl.transit_link and
    tr."type" = m.mode_id
;

DROP VIEW IF EXISTS  v_transit_trips_ttime_binned;
CREATE VIEW v_transit_trips_ttime_binned as
SELECT "agency", "mode_name", 5*cast("speed_kph"/5 as int) as speed_bin_kph, count(*)
FROM "v_transit_trips_ttime"
group by "agency", "mode_name", speed_bin_kph;

DROP VIEW IF EXISTS  v_transit_trips_by_agency_mode_cap;
CREATE VIEW v_transit_trips_by_agency_mode_cap as
SELECT 
    ta.agency as agency,
    m.mode_name,
    tt."seated_capacity", 
    tt."design_capacity", 
    tt."total_capacity",
    count(*) as trip_count
FROM
    transit_modes m,
    transit_trips tt, 
    transit_patterns tp, 
    transit_routes tr,
    transit_agencies ta
WHERE
    tt.pattern_id = tp.pattern_id and 
    tp.route_id = tr.route_id AND
    tr.agency_id = ta.agency_id and
    tr."type" = m.mode_id
group by 
    ta.agency,
    tr."type",
    tt."seated_capacity", 
    tt."design_capacity", 
    tt."total_capacity"
order by
    ta.agency,
    tr."type" desc,
    tt."seated_capacity", 
    tt."design_capacity", 
    tt."total_capacity";

DROP VIEW IF EXISTS v_transit_stops_parking;
CREATE VIEW v_transit_stops_parking as	
SELECT 
    ta.agency as agency,
    "has_parking", 
    count(*)
FROM 
    "Transit_Stops" ts,
    transit_agencies ta
where
    ta.agency_id = ts.agency_id
group by
    ta.agency;

DROP VIEW IF EXISTS v_trip_pattern_match_stop_count;
create VIEW v_trip_pattern_match_stop_count as
select
    ps.pattern_id as pattern_id,
    ts.trip_id as trip_id,
    ps.stop_count as pattern_stop_count,
    ts.stop_count as trip_stop_count
FROM
    transit_trips t,
    v_trip_stop_counter ts,
    v_transit_pattern_stop_counter ps
WHERE
    ps.pattern_id = t.pattern_id AND
    ts.trip_id = t.trip_id;

DROP VIEW IF EXISTS v_pattern_mapping_match_stop_count;
create VIEW v_pattern_mapping_match_stop_count as
select
    ps.pattern_id as pattern_id,
    ps.stop_count as pattern_stop_count,
    pms.stop_count as pattern_mapping_stop_count
FROM
    v_transit_pattern_stop_counter ps,
    v_pattern_mapping_stop_counter pms
WHERE
    ps.pattern_id = pms.pattern_id;


drop table if exists sanity_check;
create table "sanity_check"(
query_name TEXT,
error_count INTEGER
);

insert into "sanity_check"
select
'select count(*) from transit_routes where agency_id not in (select agency_id from transit_agencies)',
count(*) from transit_routes where agency_id not in (select agency_id from transit_agencies);

insert into "sanity_check"
select
'select count(*) from transit_zones where agency_id not in (select agency_id from transit_agencies)',
count(*) from transit_zones where agency_id not in (select agency_id from transit_agencies);

insert into "sanity_check"
select
'select count(*) from Transit_Trips where pattern_id not in (select pattern_id from Transit_Patterns)',
count(*) from Transit_Trips where pattern_id not in (select pattern_id from Transit_Patterns);

insert into "sanity_check"
select
'select count(*) from Transit_Trips where trip_id not in (select trip_id from transit_trips_Schedule)',
count(*) from Transit_Trips where trip_id not in (select trip_id from transit_trips_Schedule);

insert into "sanity_check"
select
'select count(*) from Transit_Trips_Schedule where trip_id not in (select trip_id from transit_trips)',
count(*) from Transit_Trips_Schedule where trip_id not in (select trip_id from transit_trips);

insert into "sanity_check"
select
'select count(*) from Transit_Patterns where pattern_id not in (select pattern_id from Transit_Trips)',
count(*) from Transit_Patterns where pattern_id not in (select pattern_id from Transit_Trips);

insert into "sanity_check"
select
'select count(*) from Transit_Patterns where route_id not in (select route_id from transit_routes)',
count(*) from Transit_Patterns where route_id not in (select route_id from transit_routes);

insert into "sanity_check"
select
'select count(*) from Transit_Pattern_Links where pattern_id not in (select pattern_id from Transit_Patterns)',
count(*) from Transit_Pattern_Links where pattern_id not in (select pattern_id from Transit_Patterns);

insert into "sanity_check"
select
'select count(*) from Transit_Pattern_Links where transit_link not in (select transit_link from Transit_Links)',
count(*) from Transit_Pattern_Links where transit_link not in (select transit_link from Transit_Links);

insert into "sanity_check"
select
'select count(*) from transit_zones where agency_id not in (select agency_id from Transit_agencies)',
count(*) from transit_zones where agency_id not in (select agency_id from Transit_agencies);

insert into "sanity_check"
select
'select count(*) from transit_walk where from_node not in (select stop_id from transit_stops union all select node from node union all select dock_id from micromobility_docks)',
count(*) from transit_walk where from_node not in (select stop_id from transit_stops union all select node from node union all select dock_id from micromobility_docks);

insert into "sanity_check"
select
'select count(*) from transit_walk where to_node not in (select stop_id from transit_stops union all select node from node union all select dock_id from micromobility_docks)',
count(*) from transit_walk where to_node not in (select stop_id from transit_stops union all select node from node union all select dock_id from micromobility_docks);

insert into "sanity_check"
select
'select count(*) from transit_bike where from_node not in (select stop_id from transit_stops union all select node from nodeunion all select dock_id from micromobility_docks)',
count(*) from transit_bike where from_node not in (select stop_id from transit_stops union all select node from node union all select dock_id from micromobility_docks);

insert into "sanity_check"
select
'select count(*) from transit_bike where to_node not in (select stop_id from transit_stops union all select node from nodeunion all select dock_id from micromobility_docks)',
count(*) from transit_bike where to_node not in (select stop_id from transit_stops union all select node from node union all select dock_id from micromobility_docks);

insert into "sanity_check"
select
'select count(*) from Transit_Stops where stop_id not in (select from_node from transit_links union all select to_node from transit_links) and agency_id <>1',
count(*) from Transit_Stops where stop_id not in (select from_node from transit_links union all select to_node from transit_links) and agency_id <>1;

insert into "sanity_check"
select
'select count(*) from Transit_Stops where stop_id not in (select from_node from transit_walk union all select to_node from transit_walk)',
count(*) from Transit_Stops where stop_id not in (select from_node from transit_walk union all select to_node from transit_walk);

insert into "sanity_check"
select
'select count(*) from Transit_Routes where agency_id not in (select agency_id from transit_agencies)',
count(*) from Transit_Routes where agency_id not in (select agency_id from transit_agencies);

insert into "sanity_check"
select
'select count(*) from Transit_Routes where route_id not in (select route_id from transit_patterns)',
count(*) from Transit_Routes where route_id not in (select route_id from transit_patterns);

insert into "sanity_check"
select
'select count(*) from Transit_Fare_Rules where fare_id not in (select fare_id from Transit_Fare_Attributes)',
count(*) from Transit_Fare_Rules where fare_id not in (select fare_id from Transit_Fare_Attributes);

insert into "sanity_check"
select
'select count(*) from Transit_Fare_Rules where origin not in (select transit_zone_id from Transit_zones)',
count(*) from Transit_Fare_Rules where origin not in (select transit_zone_id from Transit_zones);

insert into "sanity_check"
select
'select count(*) from Transit_Fare_Rules where destination not in (select transit_zone_id from Transit_zones)',
count(*) from Transit_Fare_Rules where destination not in (select transit_zone_id from Transit_zones);

insert into "sanity_check"
select
'select count(*) from Transit_Stops where transit_zone_id not in (select transit_zone_id from Transit_zones)',
count(*) from Transit_Stops where transit_zone_id not in (select transit_zone_id from Transit_zones);

insert into "sanity_check"
select
'select count(*) from Transit_Stops where agency_id not in (select agency_id from transit_agencies)',
count(*) from Transit_Stops where agency_id not in (select agency_id from transit_agencies);

insert into "sanity_check"
select
'select count(*) from Transit_Patterns where pattern_id not in (select pattern_id from Transit_Pattern_Links)',
count(*) from Transit_Patterns where pattern_id not in (select pattern_id from Transit_Pattern_Links);

insert into "sanity_check"
select
'select count(*) from Transit_Links where from_node not in (select stop_id from Transit_Stops)',
count(*) from Transit_Links where from_node not in (select stop_id from Transit_Stops);

insert into "sanity_check"
select
'select count(*) from Transit_Links where to_node not in (select stop_id from Transit_Stops)',
count(*) from Transit_Links where to_node not in (select stop_id from Transit_Stops);

insert into "sanity_check"
select
'select count(*) from Transit_Links where transit_link not in (select transit_link from Transit_Pattern_Links)',
count(*) from Transit_Links where transit_link not in (select transit_link from Transit_Pattern_Links);

insert into "sanity_check"
select
'SELECT count(*) FROM "Micromobility_Docks" where dock_id not in (select from_node from transit_walk union all select to_node from transit_walk)',
count(*) FROM "Micromobility_Docks" where dock_id not in (select from_node from transit_walk union all select to_node from transit_walk);

insert into "sanity_check"
select
'SELECT count(*) FROM "Micromobility_Docks" where dock_id not in (select from_node from transit_bike union all select to_node from transit_bike)',
count(*) FROM "Micromobility_Docks" where dock_id not in (select from_node from transit_bike union all select to_node from transit_bike);

insert into "sanity_check"
select 'select count(*) from Transit_Trips_Schedule t1, Transit_Trips_Schedule t2 where t1.trip_id = t2.trip_id and t1."index"+1 = t2."index" and (t2.arrival - t1.arrival <= 0 or t2.departure-t1.departure <= 0)',
count(*) from Transit_Trips_Schedule t1, Transit_Trips_Schedule t2 where t1.trip_id = t2.trip_id and t1."index"+1 = t2."index" and (t2.arrival - t1.arrival <= 0 or t2.departure-t1.departure <= 0);


insert into "sanity_check"
select 'select count(*) FROM "v_trip_pattern_match_stop_count" where pattern_stop_count <> trip_stop_count',
count(*) FROM "v_trip_pattern_match_stop_count" where pattern_stop_count <> trip_stop_count;

insert into "sanity_check"
select
'select count(*) FROM "v_pattern_mapping_match_stop_count" where pattern_stop_count <> pattern_mapping_stop_count',
count(*) FROM "v_pattern_mapping_match_stop_count" where pattern_stop_count <> pattern_mapping_stop_count;

   




    

    

    