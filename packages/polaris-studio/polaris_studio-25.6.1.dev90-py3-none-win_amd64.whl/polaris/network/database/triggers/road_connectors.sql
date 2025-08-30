-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--##
create trigger if not exists polaris_road_connector_populates_fields_on_new_record after insert on Road_Connectors
begin
    update  Road_Connectors
    set "length" = round(coalesce(ST_Length(new.geo), 0), 8),
        "bearing_a" =  coalesce(round(Degrees(ST_Azimuth(StartPoint(new.geo), ST_PointN(SanitizeGeometry(new.geo), 2))),0),0),
        "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0)
    where Road_Connectors.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Road_Connectors', 'geo');
end;

--##
create trigger if not exists polaris_road_connector_on_geo_change after update of "geo" on Road_Connectors
begin
    update  Road_Connectors
    set "length" = round(coalesce(ST_Length(new.geo), 0), 8),
        "bearing_a" =  coalesce(round(Degrees(ST_Azimuth(StartPoint(new.geo), ST_PointN(SanitizeGeometry(new.geo), 2))),0),0),
        "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0)
    where Road_Connectors.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_road_connector_on_length_change after update of "length" on Road_Connectors
begin
    update  Road_Connectors
    set "length" = round(coalesce(ST_Length(new.geo), 0), 8)
    where Road_Connectors.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_road_connector_on_bearing_a_change after update of "bearing_a" on Road_Connectors
begin
    update  Road_Connectors
    set "bearing_a" =  coalesce(round(Degrees(ST_Azimuth(StartPoint(new.geo), ST_PointN(SanitizeGeometry(new.geo), 2))),0),0)
    where Road_Connectors.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_road_connector_on_bearing_b_change after update of "bearing_b" on Road_Connectors
begin
    update  Road_Connectors
    set "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0)
    where Road_Connectors.rowid = new.rowid;
end;
