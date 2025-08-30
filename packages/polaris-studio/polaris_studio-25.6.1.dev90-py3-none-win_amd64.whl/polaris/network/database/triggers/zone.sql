-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
create trigger if not exists polaris_zone_on_delete_record after delete on Zone
begin
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Zone', 'geo');
end;

--##
create trigger if not exists polaris_zone_populates_fields_on_new_record after insert on Zone
begin
    update Zone
    set "x" = round(COALESCE(ST_X(ST_Centroid(new.geo)), 0), 8),
        "y" = round(COALESCE(ST_Y(ST_Centroid(new.geo)), 0), 8),
        "area" = round(COALESCE(ST_Area(new.geo), 0), 8)
    where Zone.rowid = new.rowid;

    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Zone', 'geo');
end;

--##
create trigger if not exists polaris_zone_on_x_change after update of "x" on Zone
begin
    update Zone
    set "x" = round(COALESCE(ST_X(ST_Centroid(new.geo)), new.x), 8)
    where Zone.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_zone_on_area_change after update of "area" on Zone
begin
    update Zone
    set "area" = round(COALESCE(ST_Area(new.geo), new.area), 8)
    where Zone.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_zone_on_y_change after update of "y" on Zone
begin
    update Zone
    set "y" = round(COALESCE(ST_Y(ST_Centroid(new.geo)), new.y), 8)
    where Zone.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_zone_on_geo_change after update of geo on Zone
begin
        update Zone
    set "x" = round(COALESCE(ST_X(ST_Centroid(new.geo)), old.x), 8),
        "y" = round(COALESCE(ST_Y(ST_Centroid(new.geo)), old.y), 8),
        "area" = round(COALESCE(ST_Area(new.geo), old.area), 8)
    where Zone.rowid = new.rowid;

    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Zone', 'geo');
end;

--##
create trigger if not exists polaris_zone_on_zone_change after update of "zone" on Zone
begin
    update EV_Charging_Stations set zone=new.zone where zone=old.zone;
    update Location set zone=new.zone where zone=old.zone;
    update Node set zone=new.zone where zone=old.zone;
    update Parking set zone=new.zone where zone=old.zone;
    update Transit_Stops set zone=new.zone where zone=old.zone;
    update Micromobility_Docks set zone=new.zone where zone=old.zone;
end;

--##
create trigger if not exists polaris_zone_on_area_type_change after update of area_type on Zone
begin
    update Location set area_type=new.area_type where zone=new.zone;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Zone', 'area_type');
end;