-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_micromobility_docks_populates_fields_on_new_record after insert on Micromobility_Docks
begin
    update Micromobility_Docks
        set
            "x" = round(ST_X(new.geo), 8),
            "y" = round(ST_Y(new.geo), 8),
            zone = (SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1),
            link=(SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
            offset = round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2),
            setback = round(st_distance(new.geo, (select geo from Link where link= new.link)), 2)
    where Micromobility_Docks.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_micromobility_docks_on_x_change after update of "x" on Micromobility_Docks
begin
    update Micromobility_Docks
    set "x" = round(ST_X(new.geo), 8)
    where Micromobility_Docks.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_micromobility_docks_on_y_change after update of "y" on Micromobility_Docks
begin
    update Micromobility_Docks
    set "y" = round(ST_Y(new.geo), 8)
    where Micromobility_Docks.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_micromobility_docks_on_zone_change after update of "zone" on Micromobility_Docks
begin
    update Micromobility_Docks
        set
            zone = (SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1)
    where Micromobility_Docks.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_micromobility_docks_on_link_change after update of "link" on Micromobility_Docks
begin
    update Micromobility_Docks
        set
            link=(SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
            offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset),
            setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), old.setback), 2)
    where Micromobility_Docks.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_micromobility_docks_on_offset_change after update of "offset" on Micromobility_Docks
begin
    update Micromobility_Docks
        set
            offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset)
    where Micromobility_Docks.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_micromobility_docks_on_setback_change after update of "setback" on Micromobility_Docks
begin
    update Micromobility_Docks
        set
            setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), old.setback), 2)
    where Micromobility_Docks.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_micromobility_docks_on_geo_change after update of geo on Micromobility_Docks
begin
    update Micromobility_Docks
        set
            "x" = round(ST_X(new.geo), 8),
            "y" = round(ST_Y(new.geo), 8),
            zone = (SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1),
            link=(SELECT fid FROM knn2 WHERE f_table_name = 'Link' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1),
            offset = coalesce(round((select ST_Line_Locate_Point(geo, new.geo) * "length" from Link where link=new.link), 2), old.offset),
            setback = round(coalesce(st_distance(new.geo, (select geo from Link where link= new.link)), old.setback), 2)
    where Micromobility_Docks.rowid = new.rowid;

    update Transit_Walk
    set geo = SetStartPoint(geo,new.geo)
    where from_node = new.dock_id
    and StartPoint(geo) != new.geo;

    update Transit_Walk
    set geo = SetEndPoint(geo,new.geo)
    where to_node = new.dock_id
    and EndPoint(geo) != new.geo;

    update Transit_Bike
    set geo = SetStartPoint(geo,new.geo)
    where from_node = new.dock_id
    and StartPoint(geo) != new.geo;

    update Transit_Bike
    set geo = SetEndPoint(geo,new.geo)
    where to_node = new.dock_id
    and EndPoint(geo) != new.geo;
end;

--##
create trigger if not exists polaris_micromobility_docks_enforce_unique_tag before insert on Micromobility_Agencies
when (select count(*) from Transit_Agencies where agency_id=new.agency_id)>0
begin
    SELECT raise(ABORT, 'Operator ID already used for transit agencies');
end;

--##
create trigger if not exists polaris_micromobility_docks_enforce_unique_tag_also before insert on Transit_Agencies
when (select count(*) from Micromobility_Agencies where agency_id=new.agency_id)>0
begin
    SELECT raise(ABORT, 'Operator ID already used for Micro-mobility agency');
end;