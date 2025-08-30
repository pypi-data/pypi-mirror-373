-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DROP TABLE IF EXISTS ttime_By_ACT_Average;
CREATE TABLE IF NOT EXISTS ttime_By_ACT_Average As
SELECT activity.type as acttype, 
       avg(trip.skim_travel_time)/60 as ttime_avg_skim, 
       avg(trip.routed_travel_time)/60 as ttime_avg_routed, 
       avg(trip.end - trip.start)/60 as ttime_avg, 
       avg(trip.travel_distance)/1000 as dist_avg, 
       scaling_factor*count(*) as count
FROM trip, person, household, activity
WHERE trip.person = person.person 
AND person.household = household.household 
AND person.age > 16 
AND activity.trip = trip.trip_id 
AND travel_distance < 1000000 
AND trip.end - trip.start > 2
GROUP BY ACTTYPE;

DROP TABLE IF EXISTS ttime_By_ACT_Average_w_skims;
CREATE TABLE IF NOT EXISTS ttime_By_ACT_Average_w_skims As
select activity.type as acttype, 
       avg(trip.skim_travel_time)/60 as ttime_avg_skim, 
       avg(trip.routed_travel_time)/60 as ttime_avg_routed, 
       avg(trip.end - trip.start)/60 as ttime_avg, 
       avg(trip.travel_distance)/1000 as dist_avg, 
       scaling_factor*count(*) as count
from trip, person, household, activity
where trip.person = person.person 
and person.household = household.household 
and person.age > 16 
and activity.trip = trip.trip_id 
and travel_distance < 1000000 
and trip.end - trip.start >= 0
and trip.skim_travel_time >= 0
and trip.skim_travel_time < 86400
group by ACTTYPE;

DROP TABLE IF EXISTS ttime_By_ACT_Average_w_skims_hway;
CREATE TABLE IF NOT EXISTS ttime_By_ACT_Average_w_skims_hway As
select trip.mode, 
       activity.type as acttype, 
       avg(trip.skim_travel_time)/60 as ttime_avg_skim, 
       avg(trip.routed_travel_time)/60 as ttime_avg_routed, 
       avg(trip.end - trip.start)/60 as ttime_avg, 
       avg(trip.travel_distance)/1000 as dist_avg, 
       scaling_factor*count(*) as count
from trip, person, household, activity
where trip.person = person.person 
and person.household = household.household 
and person.age > 16 
and activity.trip = trip.trip_id 
and travel_distance < 1000000 
and trip.end - trip.start >= 0
and trip.skim_travel_time >= 0
and trip.skim_travel_time < 86400
and trip.mode in (0,9)
group by trip.mode, ACTTYPE;

DROP TABLE IF EXISTS work_straight_line_dist_Average;
CREATE TABLE IF NOT EXISTS work_straight_line_dist_Average As
SELECT avg(sqrt(pow(work_loc.x - home_loc.x, 2.0) + pow(work_loc.y - home_loc.y, 2.0))) / 1000 as dist_avg, 
       scaling_factor*count(*) as count
FROM person, household, a.location as home_loc, a.location as work_loc
WHERE person.household = household.household
and household.location = home_loc.location
and person.work_location_id = work_loc.location
and home_loc.location <> work_loc.location;