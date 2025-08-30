-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
-- Comment line is the error message we will insert the error info in

-- NETWORK CHECKS;
-- Link(s) has(ve) POSITIVE fspd_ab and ZERO lanes_ab for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where l.fspd_ab > 0 and l.lanes_ab = 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) ZERO fspd_ab and POSITIVE lanes_ab for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where l.fspd_ab = 0 and lanes_ab > 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) POSITIVE fspd_ba and ZERO lanes_ba for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where l.fspd_ba > 0 and lanes_ba = 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) ZERO fspd_ba and POSITIVE lanes_ba for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where l.fspd_ba = 0 and lanes_ba > 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) fspd_ab higher than 120kph [{}]
Select "link" from Link where fspd_ab > 120;

-- Link(s) has(ve) fspd_ba higher than 120kph [{}]
Select "link" from Link where fspd_ba > 120;

-- Location_Links(s) separated by more than 4000m [{}]
Select "location" from Location_Links where distance > 4000;

-- Some unused stops on Transit_Stops [{}]
select stop_id from Transit_Stops where stop_id not in (select from_node from transit_links union all select to_node from transit_links) and agency_id>1;

-- Some missing or extra stops in the transit_pattern_mapping table [{}]
select r.pattern_id from (select pattern_id, count(*) stop_map from transit_pattern_mapping where stop_id is not null GROUP by pattern_id) as r join (select pattern_id, count(*) +1 stop_pat from Transit_Links GROUP by pattern_id) as p on r.pattern_id=p.pattern_id where abs(r.stop_map - p.stop_pat) > 0;

-- Link(s) has(ve) POSITIVE cap_ab and ZERO lanes_ab for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where cap_ab > 0 and lanes_ab = 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Link(s) has(ve) POSITIVE cap_ba and ZERO lanes_ba for link(s) [{}]
select "link" from Link l inner join link_type lt on l.type=lt.link_type where cap_ba > 0 and lanes_ba = 0 and (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%');

-- Location CHECKS;
-- Zone(s) with NO employment location has(ve) employment bigger than zero [{}]
select zone from Zone where employment_total>0 and zone not in (select zone from (select zone, sum(is_work) work_locations from Location lo inner join land_use lu on lo.land_use=lu.land_use group by zone) where work_locations>0);

-- Transit_Fare_Attributes has {} fare(s) that does not have correct transfer pricing setting
select count(cnt) from (select count(transfer) cnt, max(transfer) mx from Transit_Fare_Attributes group by fare_id) where mx>=cnt;

-- The Connections table has {} connection(s) on nodes that is not in the network
select count(*) from Connection where node not in (Select node from Node);

-- The Connections table has {} connection(s) that refer links in the network that do not exist
select count(*) from Connection where link not in (Select link from Link);

-- The Connections table has {} connection(s) that refer links in the network that do not exist
select count(*) from Connection where to_link not in (Select link from Link);

-- The Connections table has {} connection(s) going into links for which there are no lanes
select count(*) from Connection where dir=1 and link not in (Select link from Link where lanes_ba>0);

-- The Connections table has {} connection(s) going into links for which there are no lanes
select count(*) from Connection where dir=0 and link not in (Select link from Link where lanes_ab>0);

-- The Connections table has {} connection(s) going into links for which there are no lanes
select count(*) from Connection where to_dir=1 and to_link not in (Select link from Link where lanes_ba>0);

-- The Connections table has {} connection(s) going into links for which there are no lanes
select count(*) from Connection where to_dir=0 and to_link not in (Select link from Link where lanes_ab>0);

-- {} link(s) have tolling intervals in Toll pricing that do not cover the entire day
Select count(*) from (select  link, dir, sum(end_time - start_time) coverage from Toll_Pricing group by link, dir) where coverage < 86400;

-- THE NETWORK HAS ZERO TRAFFIC SIGNALS. IS THAT CORRECT?
SELECT COUNT(*)=0 FROM Signal;

-- THE NETWORK HAS ZERO STOP SIGNS. IS THAT CORRECT?
SELECT COUNT(*)=0 FROM Sign;

-- {} locations(s) have county field filled but land_use equal to EXTERNAL. This will create problems for the freight model
SELECT COUNT(*) FROM Location WHERE county IS NOT NULL AND land_use = 'EXTERNAL';