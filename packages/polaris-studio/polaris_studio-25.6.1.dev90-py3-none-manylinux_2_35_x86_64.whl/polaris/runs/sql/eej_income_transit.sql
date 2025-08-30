-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
drop table if exists executed_activity_mode_share_by_income;
create table executed_activity_mode_share_by_income as
Select
    case 
      when household.income <= 27026 then 'QUINTILE_1'
      when household.income <= 52179 and  household.income > 27026 then 'QUINTILE_2'
      when household.income <= 85076 and  household.income > 52179 then 'QUINTILE_3'
      when household.income <= 141110 and  household.income > 85076 then 'QUINTILE_4'
      when household.income > 141110 then 'QUINTILE_5'
    end as INCOME_QUINTILE,
    sum (case when activity.mode in ('BUS', 'RAIL', 'PARK_AND_RAIL', 'PARK_AND_RIDE', 'RAIL_AND_UNPARK', 'RIDE_AND_UNPARK') then 1.0 else 0.0 end)/(count(*) + 0.0) as transit_share,
    sum (case when activity.mode in ('TAXI') then 1.0 else 0.0 end)/(count(*) + 0.0) as tnc_share,
    sum (case when activity.mode in ('SOV', 'HOV') then 1.0 else 0.0 end)/(count(*) + 0.0) as auto_share,
    sum (case when activity.mode in ('WALK', 'BIKE') then 1.0 else 0.0 end)/(count(*) + 0.0) as active_share,  
    sum (case when activity.mode not in ('BUS', 'RAIL', 'PARK_AND_RAIL', 'PARK_AND_RIDE', 'RAIL_AND_UNPARK', 'RIDE_AND_UNPARK', 'TAXI', 'SOV', 'HOV', 'WALK', 'BIKE') then 1.0 else 0.0 end)/(count(*) + 0.0) as other_share
FROM
    activity, person, trip, household
WHERE
    activity.start_time > 122 and 
    activity.trip = trip.trip_id and
    trip."end" - trip."start" > 2 and
    activity.person = person.person and
    person.household = household.household and
    activity.mode not like 'FAIL%'
GROUP BY
    INCOME_QUINTILE;


-- drop table if exists avg_wait_and_total_time_by_income;
-- create table avg_wait_and_total_time_by_income as
-- select 
--     case 
--       when household.income <= 27026 then 'QUINTILE_1'
--       when household.income <= 52179 and  household.income > 27026 then 'QUINTILE_2'
--       when household.income <= 85076 and  household.income > 52179 then 'QUINTILE_3'
--       when household.income <= 141110 and  household.income > 85076 then 'QUINTILE_4'
--       when household.income > 141110 then 'QUINTILE_5'
--     end as INCOME_QUINTILE,
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