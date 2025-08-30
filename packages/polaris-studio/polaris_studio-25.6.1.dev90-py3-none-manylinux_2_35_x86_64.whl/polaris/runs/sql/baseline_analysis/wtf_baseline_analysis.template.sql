-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DROP TABLE IF EXISTS employment_validation;
CREATE TABLE employment_validation as 
select l.zone, count(*)*scaling_factor, z.employment_total
from person p, a.location l, a.zone z
where p.work_location_id = l.location  and l.zone = z.zone
group by l.zone;

DROP TABLE IF EXISTS vmt_vht_by_mode_city;
CREATE TABLE vmt_vht_by_mode_city as
SELECT mode, 
       scaling_factor*sum(travel_distance)/1609.3/1000000.0 as million_VMT, 
       scaling_factor*sum(end-start)/3600.0/1000000.0 as million_VHT, 
       scaling_factor*sum(travel_distance)/1609.3/(scaling_factor*sum(end-start)/3600.0) as speed_mph, 
       scaling_factor*count(*) as count
FROM trip t, a.location as al, a.zone as az
where t."end" > t.start and t.origin = al.location and al.zone = az.zone and az.area_type <= 3 and has_artificial_trip <> 1
group BY mode;

DROP TABLE IF EXISTS trips_in_network_city;
CREATE TABLE trips_in_network_city as
select time, cum_depart, cum_arrive, cum_depart-cum_arrive as in_network 
from (select time, 
             scaling_factor*sum(departures) OVER (ROWS UNBOUNDED PRECEDING) as cum_depart, 
         scaling_factor*sum(arrivals) OVER (ROWS UNBOUNDED PRECEDING) as cum_arrive 
      from ( select time, sum(departures) as departures, sum(arrivals) as arrivals 
             from (select cast("start"/6 as int)*6 as time, count(*) as departures, 0 as arrivals 
               from trip t, a.location l1, a.location l2
                   where mode = 0 and person is not null and t.origin = l1.location and t.destination = l2.location 
             and (l1.area_type <= 3 or l2.area_type <= 3)
             group by time
                   UNION
             select cast("end"/6 as int)*6 as time, 0 as departures, count(*) as arrivals
             from trip t, a.location l1, a.location l2
             where mode = 0 and person is not null and t.origin = l1.location and t.destination = l2.location 
             and (l1.area_type <= 3 or l2.area_type <= 3)
             group by time
             UNION
             select cast("start"/6 as int)*6 as time, count(*) as departures, 0 as arrivals
             from tnc_trip t, a.location l1, a.location l2
             where t.origin = l1.location and t.destination = l2.location and (l1.area_type <= 3 or l2.area_type <= 3)
             group by time
             UNION
             select cast("end"/6 as int)*6 as time, 0 as departures, count(*) as arrivals
             from tnc_trip t, a.location l1, a.location l2
             where t.origin = l1.location and t.destination = l2.location and (l1.area_type <= 3 or l2.area_type <= 3)
             group by time
              )
             group by time
           )
     )
;

DROP TABLE IF EXISTS planned_activity_mode_share;
CREATE TABLE planned_activity_mode_share as
Select
    activity.mode, scaling_factor*count(*) as mode_count
FROM
    activity, person
WHERE
    activity.start_time > 122 and 
    activity.trip = 0 and
    activity.person = person.person and
    person.age > 16
GROUP BY
    activity.mode;

DROP TABLE IF EXISTS executed_activity_mode_share;
CREATE TABLE executed_activity_mode_share as
Select
    activity.mode as mode, scaling_factor*count(*) as mode_count
FROM
    activity, person, trip
WHERE
    activity.start_time > 122 and 
    activity.trip = trip.trip_id and
    trip."end" - trip."start" > 2 and
    activity.person = person.person and
    person.age > 16 and
    activity.mode not like 'FAIL%'
GROUP BY
    activity.mode;

DROP TABLE IF EXISTS executed_activity_mode_share_fails;
CREATE TABLE executed_activity_mode_share_fails as
Select
    activity.mode as mode, scaling_factor*count(*) as mode_count
FROM
    activity, person
WHERE
    activity.start_time > 122 and 
    activity.trip <> 0 and
    activity.person = person.person and
    person.age > 16
GROUP BY
    activity.mode;

DROP TABLE IF EXISTS planned_activity_mode_share_by_area;
CREATE TABLE planned_activity_mode_share_by_area as
Select
    activity.type, a.zone.area_type, activity.mode, scaling_factor*count(*) as mode_count
FROM
    activity, person, a.location, a.zone
WHERE
    activity.start_time > 122 and
    activity.trip = 0 and
    activity.person = person.person and
    person.age > 16 and
    activity.location_id = a.location.location and a.location.zone = a.zone.zone
GROUP BY
    activity.type, a.zone.area_type, activity.mode;
    
DROP TABLE IF EXISTS executed_activity_mode_share_by_area;
CREATE TABLE executed_activity_mode_share_by_area as
Select
    activity.type, a.zone.area_type, activity.mode, scaling_factor*count(*) as mode_count
FROM
    activity, person, a.location, a.zone
WHERE
    activity.start_time > 122 AND
    activity.trip > 0 AND
    activity.person = person.person AND
    person.age > 16 AND
    activity.location_id = a.location.location and a.location.zone = a.zone.zone
GROUP BY
    activity.type, a.zone.area_type, activity.mode;
    
DROP TABLE IF EXISTS executed_activity_dist_by_area;
CREATE TABLE executed_activity_dist_by_area as
select type, sum(mode_count) as mode_count 
from "executed_activity_mode_share_by_area"
group by type;

DROP TABLE IF EXISTS executed_activity_dist_by_area_city;
CREATE TABLE executed_activity_dist_by_area_city as
select type, sum(mode_count) as mode_count 
from "executed_activity_mode_share_by_area"
where area_type < 4
group by type;

DROP TABLE IF EXISTS there_is_path;
CREATE TABLE there_is_path AS
SELECT path IS NOT NULL AS there_is_path,
       sum(abs(end-start-routed_travel_time))/sum(end-start) as relative_gap_abs,
       sum(max(end-start-routed_travel_time,0))/sum(end-start) as relative_gap_min0,
       count(*) as "number_of_trips" 
FROM trip
WHERE (mode = 0 or mode = 9 or mode = 17 or mode = 18 or mode = 19 or mode = 20)  and has_artificial_trip = 0
GROUP BY there_is_path;

DROP TABLE IF EXISTS gap_bins;
CREATE TABLE gap_bins AS
SELECT cast(experienced_gap/0.1 as int)*0.1 as gap_bin, path is not null as there_is_path, count(*) 
FROM trip
WHERE (mode = 0 or mode = 9 or mode = 17 or mode = 18 or mode = 19 or mode = 20) and has_artificial_trip = 0
GROUP BY gap_bin, there_is_path
ORDER BY gap_bin, there_is_path DESC;


DROP TABLE IF EXISTS greater_routed_time;
CREATE TABLE greater_routed_time as
select routed_travel_time > (end-start) as greater_routed_time, count(*)
from trip
where (mode = 0 or mode = 9 or mode = 17 or mode = 18 or mode = 19 or mode = 20) and has_artificial_trip = 0
group by greater_routed_time;

DROP TABLE IF EXISTS mode_count;
CREATE TABLE mode_count as
select mode_fn as MODE_NAME, has_artificial_trip, scaling_factor*count(*) as mode_count from trip
group by MODE_NAME, has_artificial_trip
order by MODE_NAME, has_artificial_trip;


DROP table IF EXISTS toll_revenue;
CREATE TABLE toll_revenue as
SELECT person_toll, person_toll_count, tnc_toll, tnc_toll_count, 
person_toll + tnc_toll as total_toll, person_toll_count + tnc_toll_count as total_count
FROM
    (
        SELECT scaling_factor * sum(toll) as person_toll, scaling_factor * count(*) as person_toll_count
        FROM Trip
        WHERE type = 22 or ((mode == 0 or mode == 9) and type == 11)
    ) as t1,
    (
        SELECT scaling_factor * sum(toll) as tnc_toll, scaling_factor * count(*) as tnc_toll_count
        FROM TNC_Trip
    ) as t2;
    