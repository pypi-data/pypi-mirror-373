-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--##
create trigger if not exists polaris_popsyn_region_populates_fields_on_new_record after insert on PopSyn_Region
begin
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('PopSyn_Region', 'geo');
end;

--##
create trigger if not exists polaris_popsyn_region_on_geo_change after update of geo on PopSyn_Region
begin
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('PopSyn_Region', 'geo');
end;

--##
create trigger if not exists polaris_popsyn_region_on_delete_record after delete on PopSyn_Region
begin
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('PopSyn_Region', 'geo');
end;