-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_parking_populates_fields_on_new_record after insert on Parking
begin
    update Parking
    set
        zone =(SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 50 AND expand=1 AND max_items=1),
        link=coalesce((SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),-1),
        walk_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Walk' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
        bike_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Bike' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1)
    where
        Parking.rowid = new.rowid;

    update Parking
    set
        offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), new.offset),
        setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), 0), 8),
        walk_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Walk where walk_link=new.walk_link), 2), new.walk_offset),
        bike_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Bike where bike_offset=new.bike_offset), 2), new.bike_offset)
    where
        Parking.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Parking', 'geo');
end;

--##
create trigger if not exists polaris_parking_on_link_change after update of link on Parking
when old.link!= new.link
begin
    update Parking
        set
            link=coalesce((SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1), old.link)
    where Parking.rowid = new.rowid;

    update Parking
        set
            offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset),
            setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), old.setback), 2)
    where Parking.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_parking_on_setback_change after update of setback on Parking
begin
    update Parking
    set
        setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), old.setback), 2)
    where Parking.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_parking_on_offset_change after update of offset on Parking
begin
    update Parking
    set
        offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset)
    where Parking.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_parking_on_geo_change after update of geo on Parking
begin
    update Parking
    set
        zone =(SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 50 AND expand=1 AND max_items=1),
        link=coalesce((SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1), old.link),
        walk_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Walk' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
        bike_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Bike' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1)
    where
        Parking.rowid = new.rowid;

    update Parking
    set
        offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset),
        setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), 0), 8),
        walk_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Walk where walk_link=new.walk_link), 2), old.walk_offset),
        bike_offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Bike where bike_offset=new.bike_offset), 2), old.bike_offset)
    where
        Parking.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Parking', 'geo');
end;

--##
create trigger if not exists polaris_parking_on_walk_link_change after update of walk_link on Parking
begin
    update Parking
        set
            walk_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Walk' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
            walk_offset = round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Walk where walk_link=new.walk_link), 2)
    where Parking.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_parking_on_walk_offset_change after update of walk_offset on Parking
begin
    update Parking
        set
            walk_offset = round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Walk where walk_link=new.walk_link), 2)
    where Parking.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_parking_on_bike_link_change after update of bike_link on Parking
begin
    update Parking
        set
            bike_link=(SELECT fid FROM knn2 WHERE f_table_name = 'Transit_Bike' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
            bike_offset = round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Bike where bike_link=new.bike_link), 2)
    where Parking.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_parking_on_bike_offset_change after update of bike_offset on Parking
begin
    update Parking
        set
            bike_offset = round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Transit_Bike where bike_link=new.bike_link), 2)
    where Parking.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_parking_on_zone_change after update of zone on Parking
when old.zone!= new.zone
begin
    update Parking
        set
            zone = (SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1)
    where Parking.rowid = new.rowid;
end;


--##
create trigger if not exists polaris_parking_on_delete_record after delete on Parking
begin
    DELETE FROM Location_Parking where parking=old.parking;
end;
