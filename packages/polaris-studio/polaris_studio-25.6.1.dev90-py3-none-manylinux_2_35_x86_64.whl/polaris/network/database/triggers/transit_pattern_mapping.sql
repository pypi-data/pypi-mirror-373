-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--##
create trigger if not exists polaris_transit_pattern_mapping_on_offset_change after update of "offset" on transit_pattern_mapping
begin
    update transit_pattern_mapping
    set "offset" = round(new.offset, 8)
    where transit_pattern_mapping.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_transit_mapping_populates_fields_on_new_record after insert on transit_pattern_mapping
begin
    update transit_pattern_mapping
    set "offset" = round(new.offset, 8)
    where transit_pattern_mapping.rowid = new.rowid;
end;