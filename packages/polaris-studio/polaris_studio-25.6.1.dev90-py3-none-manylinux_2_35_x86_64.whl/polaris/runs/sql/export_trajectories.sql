-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--.headers on 
--.mode csv 
--.output "trajectory_transit.csv" 
drop table if exists transit_trajectory;
create table transit_trajectory as
select
    a.value_transit_vehicle_trip as trip,  
    a.value_transit_vehicle_trip + 100000000 as vehicle,  
    10009 as veh_type, 
    'TRANSIT_BUS' as mode,
    a.value_transit_vehicle_stop_sequence as link_number,  
    a.value_link as link_id,    
    a.value_dir as link_dir,    
    a.value_act_departure_time as entering_time,    
    a.value_act_travel_time as travel_time,    
    round(a.value_start_position,2) as start_position,    
    round(a.value_length,2) as length,    
    round(a.value_speed,2) as actual_speed,    
    round(a.value_speed+5,2) as free_flow_speed,   
    b.value_act_dwell_time as stopped_time,  
    round(a.value_exit_position,2) as stop_position  
    
from transit_vehicle_links a, transit_vehicle_links b 
where 
    a.value_link <> -1
    and a.value_transit_vehicle_trip = b.value_transit_vehicle_trip
    and a.value_transit_vehicle_stop_sequence + 1 = b.value_transit_vehicle_stop_sequence
    and a.value_link_type = 12
;

--.exit 
