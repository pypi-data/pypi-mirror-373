-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--##
create trigger if not exists polaris_counties_populates_fields_on_new_record after insert on Counties
begin
    update Counties
    set "x" = round(COALESCE(ST_X(ST_Centroid(new.geo)), 0), 8),
        "y" = round(COALESCE(ST_Y(ST_Centroid(new.geo)), 0), 8)
    where Counties.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Counties', 'geo');
end;

--##
create trigger if not exists polaris_counties_on_x_change after update of "x" on Counties
begin
    update Counties
    set "x" = round(COALESCE(ST_X(ST_Centroid(new.geo)), new.x), 8)
    where Counties.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_counties_on_y_change after update of "y" on Counties
begin
    update Counties
    set "y" = round(COALESCE(ST_Y(ST_Centroid(new.geo)), new.y), 8)
    where Counties.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_counties_on_geo_change after update of geo on Counties
begin
    update Counties
        set "x" = round(COALESCE(ST_X(ST_Centroid(new.geo)), old.x), 8),
            "y" = round(COALESCE(ST_Y(ST_Centroid(new.geo)), old.y), 8)
        where Counties.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Counties', 'geo');
end;

--##
create trigger if not exists polaris_counties_on_county_change after update of county on Counties
begin
    update Location
        set county = new.county
        where Location.county = old.county;
end;

--##
create trigger if not exists polaris_counties_on_delete_record after delete on Counties
begin
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Counties', 'geo');
end;