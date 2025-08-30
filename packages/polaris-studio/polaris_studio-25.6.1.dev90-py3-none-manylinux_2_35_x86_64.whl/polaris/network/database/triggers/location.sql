-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_location_populates_fields_on_new_record after insert on Location
begin
    update Location
    set
        x = round(ST_X(new.geo), 8),
        y = round(ST_Y(new.geo), 8),
        zone =(SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 50 AND expand=1 AND max_items=1),
        area_type = coalesce((select area_type from Zone where zone=new.zone), -1),
        link=coalesce((SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),-1),
        walk_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Walk' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
        bike_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Bike' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
        -- if the PopSyn_Region table isn't populate, don't try to updated based on geo matching, just leave as is
        popsyn_region = (CASE WHEN EXISTS (SELECT 1 FROM PopSyn_Region) THEN
            (SELECT fid FROM knn2 WHERE f_table_name = 'PopSyn_Region' AND ref_geometry = new.geo AND radius = 1 AND expand = (CASE WHEN new.land_use = 'EXTERNAL' THEN 1 ELSE 0 END) AND max_items = 1)
            ELSE popsyn_region END),
        county = (CASE WHEN new.land_use != 'EXTERNAL'
                 THEN (SELECT fid FROM knn2 WHERE f_table_name = 'Counties' AND ref_geometry = new.geo AND radius = 50 AND expand=1 AND max_items=1)
                 ELSE NULL END)
    where
        Location.rowid = new.rowid;

    update Location
    set
        offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), new.offset),
        setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), 0), 8),
        walk_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Walk where walk_link=new.walk_link), 2), new.walk_offset),
        bike_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Bike where bike_offset=new.bike_offset), 2), new.bike_offset)
    where
        Location.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Location', 'geo');
end;


--##
create trigger if not exists polaris_location_on_x_change after update of x on Location
begin
    update Location
    set x = round(ST_X(new.geo), 8)
    where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_y_change after update of y on Location
begin
    update Location
    set y = round(ST_Y(new.geo), 8)
    where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_setback_change after update of setback on Location
begin
    update Location
    set
        link=coalesce((SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1), old.link)
    where Location.rowid = new.rowid;

    update Location
        set
            offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset),
            setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), old.setback), 2)
        where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_link_change after update of link on Location
begin
    update Location
        set
            link=coalesce((SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),-1)
        where
            Location.rowid = new.rowid;

    update Location
    set
        offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset),
        setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), old.setback), 2)
    where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_offset_change after update of offset on Location
begin
    update Location
    set
        offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset)
    where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_geo_change after update of geo on Location
begin
    update Location
    set
        "x" = round(ST_X(new.geo), 8),
        "y" = round(ST_Y(new.geo), 8),
        link=coalesce((SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1), old.link),
        zone =(SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1),
        walk_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Walk' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
        bike_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Bike' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
        -- if the PopSyn_Region table isn't populate, don't try to updated based on geo matching, just leave as is
        popsyn_region = (CASE WHEN EXISTS (SELECT 1 FROM PopSyn_Region) THEN
            (SELECT fid FROM knn2 WHERE f_table_name = 'PopSyn_Region' AND ref_geometry = new.geo AND radius = 1 AND expand = (CASE WHEN new.land_use = 'EXTERNAL' THEN 1 ELSE 0 END) AND max_items = 1)
            ELSE popsyn_region END),
        county = (CASE WHEN new.land_use != 'EXTERNAL'
                 THEN (SELECT fid FROM knn2 WHERE f_table_name = 'Counties' AND ref_geometry = new.geo AND radius = 50 AND expand=1 AND max_items=1)
                 ELSE NULL END)
    where Location.rowid = new.rowid;

    update Location
    set
        offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset),
        setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), 0), 8),
        walk_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Walk where walk_link=new.walk_link), 2), old.walk_offset),
        bike_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Bike where bike_offset=new.bike_offset), 2), old.bike_offset)
    where
        Location.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Location', 'geo');
end;

--##
create trigger if not exists polaris_location_on_popsyn_region_change after update of popsyn_region on Location
begin
    update Location
    set
        -- if the PopSyn_Region table isn't populate, don't try to updated based on geo matching, just leave as is
        popsyn_region = (CASE WHEN EXISTS (SELECT 1 FROM PopSyn_Region) THEN
            (SELECT fid FROM knn2 WHERE f_table_name = 'PopSyn_Region' AND ref_geometry = new.geo AND radius = 1 AND expand = (CASE WHEN new.land_use = 'EXTERNAL' THEN 1 ELSE 0 END) AND max_items = 1)
            ELSE popsyn_region END)
    where Location.rowid = new.rowid;
end;


--##
create trigger if not exists polaris_location_on_zone_change after update of zone on Location
begin
    update Location
    set
        zone =(SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1)
    where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_county_change after update of county on Location
begin
    update Location
    set
        county = (CASE WHEN new.land_use != 'EXTERNAL'
                 THEN (SELECT fid FROM knn2 WHERE f_table_name = 'Counties' AND ref_geometry = new.geo AND radius = 50 AND expand=1 AND max_items=1)
                 ELSE NULL END)
    where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_area_type_change after update of area_type on Location
when old.area_type!= new.area_type
begin
    update Location
        set
            area_type = coalesce((select area_type from Zone where zone=new.zone), old.area_type)
    where Location.rowid = new.rowid;
end;


--##
create trigger if not exists polaris_location_on_walk_link_change after update of walk_link on Location
begin
    update Location
        set
            walk_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Walk' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
            walk_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Walk where walk_link=new.walk_link), 2), old.walk_offset)
    where Location.rowid = new.rowid;
end;


--##
create trigger if not exists polaris_location_on_bike_link_change after update of bike_link on Location
begin
    update Location
        set
            bike_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Bike' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
            bike_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Bike where bike_offset=new.bike_offset), 2), old.bike_offset)
    where Location.rowid = new.rowid;
end;


--##
create trigger if not exists polaris_location_on_walk_offset_change after update of walk_offset on Location
begin
    update Location
        set walk_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Walk where walk_link=new.walk_link), 2), old.walk_offset)
    where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_bike_offset_change after update of bike_offset on Location
begin
    update Location
        set bike_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Bike where bike_link=new.bike_link), 2), old.bike_offset)
    where Location.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_on_delete_record after delete on Location
begin
    DELETE FROM Location_Links where location=old.location;
    DELETE FROM Location_Parking where location=old.location;
    update EV_Charging_Stations set location=-1 where location=old.location;
end;
