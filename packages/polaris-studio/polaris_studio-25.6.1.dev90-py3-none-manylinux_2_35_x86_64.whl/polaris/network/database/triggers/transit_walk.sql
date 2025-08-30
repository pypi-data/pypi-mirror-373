-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

create trigger if not exists polaris_transit_walk_on_delete_record after delete on Transit_Walk
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

    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Transit_Walk', 'geo');
  end;

--##
create trigger if not exists polaris_transit_walk_populates_fields_on_new_record after INSERT on Transit_Walk
  begin
    update Transit_Walk
    set "bearing_a" = coalesce(round(Degrees(ST_Azimuth(StartPoint(new.geo), ST_PointN(SanitizeGeometry(new.geo), 2))),0),0),
        "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0),
        "length" = round(ST_Length(new.geo), 4)
    where Transit_Walk.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Transit_Walk', 'geo');
  end;

--##
create trigger if not exists polaris_transit_walk_on_geo_change after UPDATE of geo on Transit_Walk
  begin
   update Transit_Walk
    set "bearing_a" = coalesce(round(Degrees(ST_Azimuth(StartPoint(new.geo), ST_PointN(SanitizeGeometry(new.geo), 2))),0),0),
        "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0),
        "length" = round(ST_Length(new.geo), 4)
    where Transit_Walk.rowid = new.rowid;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Transit_Walk', 'geo');
  end;

--##
create trigger if not exists polaris_transit_walk_on_walk_link_change after UPDATE of walk_link on Transit_Walk
  begin
    Update Location
    set walk_link = new.walk_link
    where walk_link = old.walk_link;

    Update Parking
    set walk_link = new.walk_link
    where walk_link = old.walk_link;
  end;

--##
create trigger if not exists polaris_transit_walk_on_bearing_a_change after update of "bearing_a" on Transit_Walk
begin
    update Transit_Walk
    set "bearing_a" =  coalesce(round(Degrees(ST_Azimuth(StartPoint(geo), ST_PointN(SanitizeGeometry(geo), 2))),0),0)
    where Transit_Walk.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_transit_walk_on_bearing_b_change after update of "bearing_b" on Transit_Walk
begin
    update Transit_Walk
    set "bearing_b" = coalesce(round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),0)
    where Transit_Walk.rowid = new.rowid;
end;
