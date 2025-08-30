-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--##
create trigger if not exists polaris_railports_populates_fields_new_record after insert on Railport
begin
    update Railport
    set "x" = round(COALESCE(ST_X(new.geo), 0), 8),
        "y" = round(COALESCE(ST_Y(new.geo), 0), 8)
    where Railport.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_railports_on_x_change after update of "x" on Railport
begin
    update Railport
    set "x" = round(COALESCE(ST_X(new.geo), new.x), 8)
    where Railport.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_railports_on_y_change after update of "y" on Railport
begin
    update Railport
    set "y" = round(COALESCE(ST_Y(new.geo), new.y), 8)
    where Railport.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_railports_on_geo_change after update of geo on Railport
begin
        update Railport
    set "x" = round(COALESCE(ST_X(new.geo), old.x), 8),
        "y" = round(COALESCE(ST_Y(new.geo), old.y), 8)
    where Railport.rowid = new.rowid;
end;
