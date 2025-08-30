-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

create trigger if not exists polaris_transit_bike_on_delete_record after delete on Transit_Bike
  begin
    Delete from Transit_Stops
    where stop_id = old.from_node and
    (select sum(n) from
           (
           SELECT count(*) n FROM Transit_Walk WHERE from_node = old.from_node OR to_node = old.from_node UNION ALL
           SELECT count(*) n FROM Transit_Bike WHERE from_node = old.from_node OR to_node = old.from_node UNION ALL
           SELECT count(*) c FROM Transit_Links WHERE from_node = old.from_node OR to_node = old.from_node UNION ALL
           SELECT count(*) c FROM Transit_Pattern_Mapping WHERE stop_id = old.from_node
           )
    ) < 1;

    Delete from Transit_Stops
    where stop_id = old.to_node and
    (select sum(n) from
           (
           SELECT count(*) n FROM Transit_Walk WHERE from_node = old.to_node OR to_node = old.to_node UNION ALL
           SELECT count(*) n FROM Transit_Bike WHERE from_node = old.to_node OR to_node = old.to_node UNION ALL
           SELECT count(*) c FROM Transit_Links WHERE from_node = old.to_node OR to_node = old.to_node UNION ALL
           SELECT count(*) c FROM Transit_Pattern_Mapping WHERE stop_id = old.to_node
           )
    ) < 1;

    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Transit_Bike', 'geo');
  end;

--##
create trigger if not exists polaris_transit_bike_populates_fields_on_new_record after INSERT on Transit_Bike
  begin
    update Transit_Bike
    set "bearing_a" =  coalesce(round(Degrees(ST_Azimuth(StartPoint(new.geo), ST_PointN(SanitizeGeometry(new.geo), 2))),0),0),
        "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0),
        "length" = round(ST_Length(new.geo), 4)
    where Transit_Bike.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Transit_Bike', 'geo');
  end;

--##
create trigger if not exists polaris_transit_bike_on_geo_change after UPDATE of geo on Transit_Bike
  begin
    update Transit_Bike
    set "bearing_a" =  coalesce(round(Degrees(ST_Azimuth(StartPoint(new.geo), ST_PointN(SanitizeGeometry(new.geo), 2))),0),0),
        "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0),
        "length" = round(ST_Length(new.geo), 4)
    where Transit_Bike.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Transit_Bike', 'geo');
  end;

--##
create trigger if not exists polaris_transit_bike_on_bike_link_change after UPDATE of bike_link on Transit_Bike
  begin
    Update Location
    set bike_link = new.bike_link
    where bike_link = old.bike_link;
  end;


--##
create trigger if not exists polaris_transit_bike_on_bearing_a_change after update of "bearing_a" on Transit_Bike
begin
    update Transit_Bike
    set "bearing_a" =  coalesce(round(Degrees(ST_Azimuth(StartPoint(geo), ST_PointN(SanitizeGeometry(geo), 2))),0),0)
    where Transit_Bike.rowid = new.rowid;
end;


--##
create trigger if not exists polaris_transit_bike_on_bearing_b_change after update of "bearing_b" on Transit_Bike
begin
    update Transit_Bike
    set "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0)
    where Transit_Bike.rowid = new.rowid;
end;
