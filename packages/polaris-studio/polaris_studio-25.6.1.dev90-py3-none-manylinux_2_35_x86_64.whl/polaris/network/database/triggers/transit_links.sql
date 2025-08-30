-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--##
create trigger if not exists polaris_transit_links_populates_fields_on_new_record after insert on Transit_Links
begin
    update Transit_Links
    set "length" = round(coalesce(ST_Length(new.geo), 0), 8)
    where Transit_Links.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_transit_links_on_geo_change after update of "geo" on Transit_Links
begin
    update Transit_Links
    set "length" = round(coalesce(ST_Length(new.geo), 0), 8)
    where Transit_Links.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_transit_links_on_length_change after update of "length" on Transit_Links
begin
    update Transit_Links
    set "length" = round(coalesce(ST_Length(new.geo), 0), 8)
    where Transit_Links.rowid = new.rowid;
end;
