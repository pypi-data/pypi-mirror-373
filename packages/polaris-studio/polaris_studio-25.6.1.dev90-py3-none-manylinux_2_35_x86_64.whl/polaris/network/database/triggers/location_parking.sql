-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_location_parking_populates_fields_on_new_record after insert on Location_Parking
begin
    update Location_Parking
    set "distance" = round(st_distance((select geo from Location where location = new.location),
                                 (select geo from Parking where parking = new.parking)), 2),
    "id" = new.rowid
    where Location_Parking.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_location_parking_populates_fields_on_table_change after update on Location_Parking
begin
    update Location_Parking
    set "distance" = round(st_distance((select geo from Location where location = new.location),
                                       (select geo from Parking where parking = new.parking)), 2),
    "id" = new.rowid
    where Location_Parking.rowid = new.rowid;
end;

