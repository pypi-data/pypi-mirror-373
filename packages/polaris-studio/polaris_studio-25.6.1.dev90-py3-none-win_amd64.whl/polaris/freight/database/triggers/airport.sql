-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--##
create trigger if not exists polaris_airport_populates_fields_new_record after insert on Airport
begin
    update Airport
    set "x" = round(COALESCE(ST_X(new.geo), 0), 8),
        "y" = round(COALESCE(ST_Y(new.geo), 0), 8)
    where Airport.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_airport_on_x_change after update of "x" on Airport
begin
    update Airport
    set "x" = round(COALESCE(ST_X(new.geo), new.x), 8)
    where Airport.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_airport_on_y_change after update of "y" on Airport
begin
    update Airport
    set "y" = round(COALESCE(ST_Y(new.geo), new.y), 8)
    where Airport.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_airport_on_geo_change after update of geo on Airport
begin
        update Airport
    set "x" = round(COALESCE(ST_X(new.geo), old.x), 8),
        "y" = round(COALESCE(ST_Y(new.geo), old.y), 8)
    where Airport.rowid = new.rowid;
end;
