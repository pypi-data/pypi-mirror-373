-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
-- Comment line is the error message we will insert the error info in

-- Checks in this file are just overall consistency checks, and a network that fails these checks WILL CRASH the run

-- NETWORK CHECKS;

-- Link(s) has(ve) POSITIVE fspd_ab and ZERO lanes_ab for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where fspd_ab > 0 and lanes_ab = 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) ZERO fspd_ab and POSITIVE lanes_ab for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where fspd_ab = 0 and lanes_ab > 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) POSITIVE fspd_ba and ZERO lanes_ba for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where fspd_ba > 0 and lanes_ba = 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) ZERO fspd_ba and POSITIVE lanes_ba for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where fspd_ba = 0 and lanes_ba > 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) no lanes on either direction: [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where l.lanes_ab + l.lanes_ba = 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) on Transit_Pattern_Mapping do(es) not exist: [{}]
select count(*) from Transit_Pattern_Mapping tpm inner join Link l on tpm.link = l.link where l.node_a is null;

-- There are {} locations with NULL for zone
select count(*) from Location where zone is null;

-- There are {} locations with NULL for link
select count(*) from Location where link is null;

-- There are {} locations with NULL for walk_link
select count(*) from Location where walk_link is null;

-- There are {} locations with non-existent walk_link
select count(wl.walk_link) from Location l inner join Transit_Walk wl on l.walk_link=wl.walk_link where wl.walk_link is null;

-- There are {} locations with non-existent bike_link
select count(wl.bike_link) from Location l inner join Transit_Bike wl on l.bike_link=wl.bike_link where wl.bike_link is null;

-- There are {} Parkings with NULL for zone
select count(*) from Parking where zone is null;

-- There are {} Parkings with NULL for link
select count(*) from Parking where link is null;

-- There are {} Parkings with NULL for walk_link
select count(*) from Parking where walk_link is null;

-- There are {} Parkings with non-existent walk_link
select count(wl.walk_link) from Parking l inner join Transit_Walk wl on l.walk_link=wl.walk_link where wl.walk_link is null;

-- There are {} Transit_Stops items with NULL for zone
select count(*) from Transit_Stops where zone is null;

-- There are {} ev_charging_stations with NULL for zone
select count(*) from ev_charging_stations where zone is null;

-- There are nodes [{}] with NULL for zone
select node from Node where zone is null;

-- There is (are) zone(s) with no Locations: [{}]
select z.zone from Zone z where z.zone not in (select distinct(zone) from Location);

-- There is (are) [{}] locations(s) with no records on Location_Links
select lo.location from Location lo LEFT join Location_Links ll on lo.location=ll.location where ll.link is NULL;

-- There is (are) [{}] phases(s) with no movements on Phasing
select count(*) from Phasing where movements=0;

-- There is (are) [{}] signals(s) with no periods associated
select count(*) from Signal where times=0;

-- There is (are) [{}] timing(s) with no nested records associated
select count(*) from Timing where phases=0;

-- There is (are) [{}] timing(s) with Cycle equal zero
select count(*) from Timing where cycle=0;

-- There is (are) node(s) [{}] that cannot be reached
select node from (
    select sum(lanes) lanes, node from (
        select sum(l.lanes_ab) lanes, l.node_b node from Link l
            INNER JOIN link_type lt on l.type=lt.link_type
                where l.lanes_ab>0 AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')
            group by l.node_b
        Union ALL
        select sum(l.lanes_ba) lanes, l.node_a node from Link l
            INNER JOIN link_type lt on l.type=lt.link_type
                where l.lanes_ba>0 AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')
            group by l.node_a)
    Link group by node)
where lanes < 1;


-- There is (are) node(s) [{}] where there is nowhere to go to
select node from (
    select sum(lanes) lanes, node from (
        select sum(l.lanes_ab) lanes, l.node_a node from Link l
            INNER JOIN link_type lt on l.type=lt.link_type
                where l.lanes_ab>0 AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')
            group by l.node_a
        Union ALL
        select sum(l.lanes_ba) lanes, l.node_b node from Link l
            INNER JOIN link_type lt on l.type=lt.link_type
                where l.lanes_ba>0 AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')
            group by l.node_b)
    Link group by node)
where lanes < 1;


--  There is (are) connections that do not have any green time in signals(s). Conn Ids: [{}]
-- select conn_id from
-- (select * from
-- (select conn conn_id, needs_phases from Connection con inner join (select nodes, count(*) needs_phases from signal sig inner join signal_nested_records snr where sig.signal = snr.object_id group by (nodes)) ccc where con.node=ccc.nodes) should_have
-- left join
-- (select conn, count(*) got_phases from (select * from Connection con inner join signal sig where con.node=sig.nodes) ccc left join phasing_nested_records pnr where ccc.link=pnr.value_link and ccc.to_link=pnr.value_to_link group by conn) does_have
-- where does_have.conn = should_have.conn_id)
-- where needs_phases > got_phases;


-- pattern_id on Transit_Trips Vs. Transit_Patterns is wrong [{}]
select count(*) from Transit_Trips where pattern_id not in (select pattern_id from Transit_Patterns);

-- trip_id on Transit_Trips Vs. transit_trips_Schedule is wrong [{}]
select count(*) from Transit_Trips where trip_id not in (select trip_id from transit_trips_Schedule);

-- trip_id on Transit_Trips_Schedule Vs. transit_trips is wrong [{}]
select count(*) from Transit_Trips_Schedule where trip_id not in (select trip_id from transit_trips);

-- pattern_id on Transit_Trips Vs. Transit_Patterns is wrong [{}]
select count(*) from Transit_Patterns where pattern_id not in (select pattern_id from Transit_Trips);

-- route_id on Transit_Patterns Vs. transit_routes is wrong [{}]
select count(*) from Transit_Patterns where route_id not in (select route_id from transit_routes);

-- pattern_id on Transit_Pattern_Links Vs. Transit_Patterns is wrong [{}]
select count(*) from Transit_Pattern_Links where pattern_id not in (select pattern_id from Transit_Patterns);

-- agency_id on transit_zones Vs. Transit_agencies is wrong [{}]
select count(*) from transit_zones where agency_id not in (select agency_id from Transit_agencies);

-- from_node on transit_walk Vs. transit_stops is wrong [{}]
select count(*) from transit_walk where from_node not in (select stop_id from transit_stops union all select dock_id from Micromobility_Docks union all select node from node);

-- to_node on transit_walk Vs. transit_stops is wrong [{}]
select count(*) from transit_walk where to_node not in (select stop_id from transit_stops union all select dock_id from Micromobility_Docks union all select node from node);

-- from_node on transit_bike Vs. transit_stops is wrong [{}]
select count(*) from transit_bike where from_node not in (select stop_id from transit_stops union all select dock_id from Micromobility_Docks union all select node from node);

-- to_node on transit_bike Vs. transit_stops is wrong [{}]
select count(*) from transit_bike where to_node not in (select stop_id from transit_stops union all select dock_id from Micromobility_Docks union all select node from node);

-- Stop IDs missing from transit_stops while present on Transit_Links [{}]
select * from (select from_node stop_id from transit_links union all select to_node stop_id from transit_links) where stop_id not in (select stop_id from Transit_Stops);

-- agency_id on Transit_Routes Vs. Transit_agencies is wrong [{}]
select count(*) from Transit_Routes where agency_id not in (select agency_id from transit_agencies);

-- route_id on Transit_Patterns Vs. transit_routes is wrong [{}]
select count(*) from Transit_Routes where route_id not in (select route_id from transit_patterns);

-- There are {} agencies for which there are no fares with transfer 0
select coalesce(sum(transfers),0) from (select min(transfer) transfers from Transit_Fare_Attributes group by agency_id);

-- fare_id on Transit_Fare_Rules Vs. Transit_Fare_Attributes is wrong [{}]
select count(*) from Transit_Fare_Rules where fare_id not in (select fare_id from Transit_Fare_Attributes);

-- origin on Transit_Fare_Rules Vs. Transit_zones is wrong [{}]
select count(*) from Transit_Fare_Rules where origin not in (select transit_zone_id from Transit_zones);

-- destination on Transit_Fare_Rules Vs. Transit_zones is wrong [{}]
select count(*) from Transit_Fare_Rules where destination not in (select transit_zone_id from Transit_zones);

-- agency_id on Transit_Stops Vs. Transit_agencies is wrong [{}]
select count(*) from Transit_Stops where agency_id not in (select agency_id from transit_agencies);

-- pattern_id on Transit_Patterns Vs. Transit_Pattern_Links is wrong [{}]
select count(*) from Transit_Patterns where pattern_id not in (select pattern_id from Transit_Pattern_Links);

-- from_node on Transit_Links Vs. Transit_Stops is wrong [{}]
select count(*) from Transit_Links where from_node not in (select stop_id from Transit_Stops);

-- to_node on Transit_Links Vs. Transit_Stops is wrong [{}]
select count(*) from Transit_Links where to_node not in (select stop_id from Transit_Stops);

-- transit_link on Transit_Links Vs. from Transit_Pattern_Links is wrong [{}]
select count(*) from Transit_Links where transit_link not in (select transit_link from Transit_Pattern_Links);

-- transit_link on Transit_Pattern_Links Vs. from Transit_Links is wrong [{}]
select count(*) from Transit_Pattern_Links where transit_link not in (select transit_link from Transit_Links);

-- There are Transit Routes with incompatible number of stop times (transit_trips_schedule) and links (transit_links) -> {}
select  distinct(pattern_id) from (
select tk.trip_id, tk.rec_stops, tk.pattern_id, tm.rec_links+1 rec_links FROM
(select tt.trip_id, rec_stops, pattern_id from (select trip_id, count(*) rec_stops from transit_trips_schedule group by trip_id) tt inner join transit_trips trp on tt.trip_id=trp.trip_id) tk
inner join (select pattern_id, count(*) rec_links from transit_links group by pattern_id) tm on tm.pattern_id=tk.pattern_id) where rec_links != rec_stops;

-- There are {} conflicting node IDs between micromobility docks and network nodes
select count(*) from Micromobility_Docks where dock_id in (select node from node);

-- There are {} conflicting node IDs between micromobility docks and transit stops
select count(*) from Micromobility_Docks where dock_id in (select stop_id from Transit_Stops);

-- There are {} conflicting node IDs between transit stops and network nodes
select count(*) from node where node in (select stop_id from Transit_Stops);

-- There are {} patterns with no stops in their first map-matched segment
SELECT count(*) FROM "Transit_Pattern_Mapping" where "index" = 0 and stop_id is null;

-- There are {} patterns where the number of transit_links does not match the number of stops in Transit_Pattern_Mapping
Select count(*) from
    (select tl.pattern_id, tl.tot_links,tpm.tot_stops, tl.tot_links-tpm.tot_stops diff from
        (select pattern_id, count(*) tot_links from transit_links group by pattern_id) as tl
            inner join
        (select pattern_id, count(*) tot_stops from Transit_pattern_mapping where stop_id not null group by pattern_id)  as tpm
        ON tl.pattern_id=tpm.pattern_id)
    where diff!=-1;

-- There are agencies with more than one fare for the same of number of transfers for the same agency -> {}
SELECT agency_id
  FROM (SELECT Count(*) - Count(DISTINCT( transfer )) repeated, agency_id
          FROM (SELECT *
                FROM Transit_Fare_Attributes
                WHERE NOT EXISTS (SELECT 1
                                  FROM Transit_Fare_Rules
                                  WHERE Transit_Fare_Rules.fare_id = Transit_Fare_Attributes.fare_id))
         GROUP BY agency_id) WHERE repeated > 0;

-- There must be a 'hand_of_driving' field in the 'About_Model' table.
select count(*) - 1  from About_Model where infoname='hand_of_driving';

-- There are parking facilities referring to links that do not exist -> {}
SELECT count(*) FROM Parking WHERE link NOT IN (SELECT link FROM Link);

-- There are Locations referring to links that do not exist -> {}
SELECT count(*) FROM Location WHERE link NOT IN (SELECT link FROM Link);

-- There are Micro-mobility Docks referring to links that do not exist -> {}
SELECT count(*) FROM Micromobility_Docks WHERE link NOT IN (SELECT link FROM Link);

-- There are EV_Charging_Stations referring to Locations that do not exist -> {}
SELECT count(*) FROM EV_Charging_Stations WHERE location NOT IN (SELECT location FROM Location);

-- There are EV_Charging_Stations referring to zones that do not exist -> {}
SELECT count(*) FROM EV_Charging_Stations WHERE zone NOT IN (SELECT zone FROM Zone);

-- There are Tolls referring to link directions that do not exist -> {}
SELECT count(*) FROM Toll_Pricing WHERE dir=0 and link NOT IN (SELECT link FROM link where lanes_ab>0);

-- There are Tolls referring to link directions that do not exist -> {}
SELECT count(*) FROM Toll_Pricing WHERE dir=1 and link NOT IN (SELECT link FROM link where lanes_ba>0);

-- There are links with speeds HIGHER than prescribed in the link_type table for their link type
SELECT count(*) FROM Link l JOIN Link_Type lt ON l.type=lt.link_type WHERE l.fspd_ab>lt.speed_limit OR l.fspd_ba>lt.speed_limit;

-- There are links with speeds LOWER than prescribed in the link_type table for their link type
SELECT count(*) FROM Link l JOIN Link_Type lt ON l.type=lt.link_type WHERE (l.lanes_ab > 0 AND l.fspd_ab<lt.minimum_speed) OR (l.lanes_ba > 0 AND l.fspd_ba<lt.minimum_speed);

-- There are Area types in the zone table that do not exist in the Polaris standard -> {}
SELECT count(*) FROM Zone WHERE area_type not in (1,2,3,4,5,6,7,8,98,99);

-- There are {} overlaps in identifiers between Links and Road_Connectors
SELECT count(*) FROM link WHERE link IN (SELECT road_connector FROM Road_Connectors);

-- There are {} non-resolved issues in the Geo_Consistency_Controller Table
SELECT count(*) FROM "Geo_Consistency_Controller";

-- There are {} tolls with negative values in the Toll_Pricing table
SELECT count(*) FROM Toll_Pricing where price<0;

-- There are {} tolls with negative values for MD in the Toll_Pricing table
SELECT count(*) FROM Toll_Pricing where md_price<0;

-- There are {} tolls with negative values for HD in the Toll_Pricing table
SELECT count(*) FROM Toll_Pricing where hd_price<0;

-- There are {} link(s) have overlapping tolling intervals in Toll pricing
SELECT count(distinct(a.link)) FROM Toll_pricing a JOIN Toll_pricing b ON a.link == b.link AND a.dir == b.dir AND a.start_time < b.end_time AND a.end_time > b.start_time AND (a.end_time != b.end_time AND a.start_time != b.start_time );

-- There are no jobs by category data in the model which will blow up destination choice
SELECT coalesce(sum(employment_retail + employment_government + employment_manufacturing + employment_services + employment_industrial + employment_other),0) == 0 FROM Zone;

-- Distribution of races in zones missing and is needed by destination choice
SELECT coalesce(sum(percent_white + percent_black),0)  == 0.0 FROM Zone;

-- There is no avg. household income data in the zone table and is needed by destination choice
SELECT coalesce(sum(hh_inc_avg),0)  == 0 FROM Zone;