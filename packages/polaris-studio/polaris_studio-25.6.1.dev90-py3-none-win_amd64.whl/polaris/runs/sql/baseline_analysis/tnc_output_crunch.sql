-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
drop table if exists TNC_Agg_Output;
CREATE TABLE TNC_Agg_Output AS SELECT tt.*, pick_wait.*, sav_req.*,
(cast (avo_t.tot_pax as real)/ cast (avo_t.tot_trips as real)) as avo_trips,
avo_d.*,
(cast (avo_t_revenue.tot_pax as real)/ cast (avo_t_revenue.tot_trips as real)) as avo_trips_revenue,
avo_d_revenue.*,
sav4.*,
cast (sav4.avg_idle_time as real)/24*100 as perc_idle,
sav5.*,
sim_p.*, p.*, sov.*, hov.*, transit.*, sav1.*, sav2.*, sav3.*, sav_unmet.unmet_dist/avo_d.avo_dist as estimated_artificial_sav_vmt,
100*(cast (sav_req.demand as real)/(cast (sav_req.demand as real) + cast (sov_req.demand as real) + cast (hov_req.demand as real) + cast (non_motor_req.demand as real) + cast (transit_req.demand as real) + cast (other_req.demand as real))) as sav_mode_share,
100*(cast (sov_req.demand as real)/(cast (sav_req.demand as real) + cast (sov_req.demand as real) + cast (hov_req.demand as real) + cast (non_motor_req.demand as real) + cast (transit_req.demand as real) + cast (other_req.demand as real))) as sov_mode_share,
100*(cast (hov_req.demand as real)/(cast (sav_req.demand as real) + cast (sov_req.demand as real) + cast (hov_req.demand as real) + cast (non_motor_req.demand as real) + cast (transit_req.demand as real) + cast (other_req.demand as real)))  as hov_mode_share,
100*(cast (non_motor_req.demand as real)/(cast (sav_req.demand as real) + cast (sov_req.demand as real) + cast (hov_req.demand as real) + cast (non_motor_req.demand as real) + cast (transit_req.demand as real) + cast (other_req.demand as real)))  as non_motor_mode_share,
100*(cast (transit_req.demand as real)/(cast (sav_req.demand as real) + cast (sov_req.demand as real) + cast (hov_req.demand as real) + cast (non_motor_req.demand as real) + cast (transit_req.demand as real) + cast (other_req.demand as real)))  as transit_mode_share,
100*(cast (other_req.demand as real)/(cast (sav_req.demand as real) + cast (sov_req.demand as real) + cast (hov_req.demand as real) + cast (non_motor_req.demand as real) + cast (transit_req.demand as real) + cast (other_req.demand as real)))  as other_mode_share
FROM
(SELECT avg(end-start)/60 as TT FROM Trip WHERE mode = 9 AND has_artificial_trip = 0) as tt,
(SELECT avg(end-start)/60 as pickup,  avg(start - request_time)/60 as wait FROM TNC_Trip WHERE final_status = -1) as pick_wait,
(SELECT count(*) as demand, 100*(1- (cast (sum(has_artificial_trip) as real)) / (cast (count(*) as real))) as perc_met
FROM Trip t
WHERE mode = 9) as sav_req,
(SELECT count(*) as demand FROM Trip t
WHERE mode = 0) as sov_req,
(SELECT count(*) as demand FROM Trip t
WHERE mode = 2) as hov_req,
(SELECT count(*) as demand FROM Trip t
WHERE mode = 7 or mode = 8) as non_motor_req,
(SELECT count(*) as demand FROM Trip t
WHERE mode = 3 or mode = 4 or mode = 5 or mode = 11 or mode = 12 or mode = 13 or mode = 14 or mode = 15 or mode = 16) as transit_req,
(SELECT count(*) as demand FROM Trip t
WHERE mode = 10 or mode > 16) as other_req,
(SELECT sum(passengers) as tot_pax, count(*) as tot_trips FROM TNC_Trip WHERE travel_distance != 0) as avo_t,
(SELECT sum(passengers*travel_distance)/sum(travel_distance) as avo_dist FROM TNC_Trip) as avo_d,
(SELECT sum(passengers) as tot_pax, count(*) as tot_trips FROM TNC_Trip WHERE travel_distance != 0 and passengers != 0) as avo_t_revenue,
(SELECT sum(passengers*travel_distance)/sum(travel_distance) as avo_dist_revenue FROM TNC_Trip WHERE passengers != 0) as avo_d_revenue,
(SELECT sum(travel_distance)/1600 as sim_pmt FROM Trip WHERE has_artificial_trip = 0) as sim_p,
(SELECT sum(travel_distance)/1600 as tot_pmt FROM Trip) as p,
(SELECT sum(travel_distance)/1600 as sov_vmt FROM Trip WHERE mode = 0) as sov,
(SELECT sum(travel_distance)/1600 as hov_vmt FROM Trip WHERE mode = 2) as hov,
(SELECT sum(value_length)/1600 as transit_vmt FROM Transit_Vehicle_links) as transit,
(SELECT sum(travel_distance)/1600 as empty_sav_vmt FROM TNC_Trip WHEre passengers = 0) as sav1,
(SELECT sum(travel_distance)/1600 as repos_vmt FROM TNC_Trip WHEre final_status = -3) as sav2,
(SELECT sum(travel_distance)/1600 as sav_vmt FROM TNC_Trip) as sav3,
(SELECT avg(idle) as avg_idle_time FROM (SELECT 24 - sum(end-start)/3600 as idle From TNC_Trip Group by vehicle)) as sav4,
(SELECT avg(trips_completed) as avg_sav_trips FROM (SELECT count(*) as trips_completed From TNC_Trip where final_status = -2 group by vehicle)) as sav5,
(SELECT sum(travel_distance)/1600 as unmet_dist FROM Trip WHERE mode == 9 and has_artificial_trip != 0) as sav_unmet;

drop table if exists TNC_AVO_Revenue_by_TOD;
CREATE TABLE TNC_AVO_Revenue_by_TOD AS SELECT tod,
cast(tot_pax as real)/cast(tot_trips as real) as avo_t_revenue, tot_trips as demand FROM (SELECT cast(start/3600 as int) as tod,
sum(passengers) as tot_pax, count(*) as tot_trips FROM TNC_Trip
WHERE travel_distance != 0 and passengers != 0 GROUP BY tod);

drop table if exists TNC_AVO_Dist_by_TOD;
CREATE TABLE TNC_AVO_Dist_by_TOD AS SELECT cast(start/3600 as int) as tod, sum(passengers * travel_distance)/sum(travel_distance) as avo_d
FROM TNC_Trip
GROUP BY tod;

drop table if exists TNC_Delay_Histogram;
CREATE TABLE TNC_Delay_Histogram AS SELECT count(*), cast(((end-start)/60)/5 as int) as tt FROM Trip
WHERE mode = 9 AND has_artificial_trip = 0 GROUP By tt;

drop table if exists TNC_Demand_by_TOD;
CREATE TABLE TNC_Demand_by_TOD AS SELECT cast(start/3600 as int) as tod, count(*) as demand
FROM Trip WHERE mode = 9 and has_artificial_trip = 0
GROUP BY tod;

drop table if exists TNC_Response_By_TOD;
CREATE TABLE TNC_Response_By_TOD AS SELECT cast(start/3600 as int) as hour, avg(end-request_time)/60 as response_time FROM TNC_Trip WHERE final_status = -1 GROUP BY hour;