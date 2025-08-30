-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_location_links_populates_fields_on_new_record after insert on Location_Links
begin
    update Location_Links
    set "distance" = round(st_distance((select geo from Location where location = new.location),
                                 (select geo from Link where link = new.link)), 2)
    where Location_Links.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_links_populates_fields_on_table_change after update on Location_Links
begin
    update Location_Links
    set "distance" = round(st_distance((select geo from Location where location = new.location),
                                 (select geo from Link where link = new.link)), 2)
    where Location_Links.rowid = new.rowid;
end;
