-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
-- COPIED DIRECTLY FROM AEQUILIBRAE with minor adaptations

-- note that sqlite only recognises 5 basic column affinities (TEXT, NUMERIC, INTEGER, REAL, BLOB); more specific declarations are ignored
-- the 'INTEGER PRIMARY KEY' column is always 64-bit signed integer, AND an alias for 'ROWID'.

-- Note that manually editing the ogc_fid will corrupt the spatial index. Therefore, we leave the
-- ogc_fid alone, and have a separate link_id and node, for network editors who have specific
-- requirements.

-- it is recommended to use the listed edit widgets in QGIS;

--
-- Triggers are grouped by the table which triggers their execution
-- 

-- Triggered by changes to link.
--

-- we use a before ordering here, as it is the only way to guarantee this will run before the node id update trigger.
-- when inserting a link end point to empty space, create a new node

--##
create trigger if not exists polaris_network_new_link_node_a before insert on link
  when
    (SELECT count(*)
    FROM node
    WHERE node.geo = StartPoint(new.geo) AND
    (node.ROWID IN (
        SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
        search_frame = StartPoint(new.geo)) OR
      node.node = new.node_a)) = 0
  BEGIN
    INSERT INTO node (node, geo)
    VALUES ((SELECT coalesce(max(node) + 1,1) FROM node),
            StartPoint(new.geo));
  END;

--##

create trigger if not exists polaris_network_new_link_node_b before insert on link
  when
    (SELECT count(*)
    FROM node
    WHERE node.geo = EndPoint(new.geo) AND
    (node.ROWID IN (
        SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
        search_frame = EndPoint(new.geo)) OR
      node.node = new.node_b)) = 0
  BEGIN
    INSERT INTO node (node, geo)
    VALUES ((SELECT coalesce(max(node) + 1,1) FROM node),
            EndPoint(new.geo));
  END;
--##

create trigger if not exists polaris_network_update_link_node_a before update of geo on link
-- we use a before ordering here, as it is the only way to guarantee this will run before the node id update trigger.
-- when inserting a link end point to empty space, create a new node
  when
    (SELECT count(*)
    FROM node
    WHERE node.geo = StartPoint(new.geo) AND
    (node.ROWID IN (
        SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
        search_frame = StartPoint(new.geo)) OR
      node.node = new.node_a)) = 0
  BEGIN
    INSERT INTO node (node, geo)
    VALUES ((SELECT coalesce(max(node) + 1,1) FROM node),
            StartPoint(new.geo));
  END;

--##

create trigger if not exists polaris_network_update_link_node_b before update of geo on link
  when
    (SELECT count(*)
    FROM node
    WHERE node.geo = EndPoint(new.geo) AND
    (node.ROWID IN (
        SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
        search_frame = EndPoint(new.geo)) OR
      node.node = new.node_b)) = 0
  BEGIN
    INSERT INTO node (node, geo)
    VALUES ((SELECT coalesce(max(node) + 1,1) FROM node),
            EndPoint(new.geo));
  END;
--##

create trigger if not exists polaris_network_new_link after insert on link
  begin
    -- Update a/node_b AFTER creating a link.
    update link
    set node_a = (
      select node
      from node
      where node.geo = StartPoint(new.geo) and
      (node.rowid in (
          select rowid from SpatialIndex where f_table_name = 'node' and
          search_frame = StartPoint(new.geo)) or
        node.node = new.node_a))
    where link.rowid = new.rowid;
    update link
    set node_b = (
      select node
      from node
      where node.geo = EndPoint(new.geo) and
      (node.rowid in (
          select rowid from SpatialIndex where f_table_name = 'node' and
          search_frame = EndPoint(new.geo)) or
        node.node = new.node_b))
    where link.rowid = new.rowid;

    update link
    set "length" = round(ST_Length(new.geo), 8),
        "bearing_b" = round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),
        "bearing_a" =  round(Degrees(ST_Azimuth(StartPoint(geo), ST_PointN(SanitizeGeometry(geo), 2))),0)
    where link.rowid = new.rowid;

    update link set
        link=(select max("link")+1 from link)
    where rowid=NEW.rowid and new.link is null;

  end;

--##

create trigger if not exists polaris_link_on_bearing_a_change after update of "bearing_a" on link
begin
    update link
    set "bearing_a" =  round(Degrees(ST_Azimuth(StartPoint(new.geo), ST_PointN(SanitizeGeometry(new.geo), 2))),0)
    where link.rowid = new.rowid;
end;


--##

create trigger if not exists polaris_link_on_bearing_b_change after update of "bearing_b" on link
begin
    update link
    set "bearing_b" = round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0)
    where link.rowid = new.rowid;
end;

--##

create trigger if not exists polaris_link_on_length_change after update of "length" on link
begin
  update link set "length" = round(ST_Length(new.geo), 8)
  where link.rowid = new.rowid;
end;

--##

create trigger if not exists polaris_link_on_geo_change after update of geo on link
  begin
  -- Update a/node_b AFTER moving a link.
  -- Note that if this TRIGGER is triggered by a node move, then the SpatialIndex may be out of date.
  -- This is why we also allow current node_a to persist.
    update link
    set node_a = (
      select node
      from node
      where node.geo = StartPoint(new.geo) and
      (node.rowid in (
          select rowid from SpatialIndex where f_table_name = 'node' and
          search_frame = StartPoint(new.geo)) or
        node.node = new.node_a))
    where link.rowid = new.rowid;
    update link
    set node_b = (
      select node
      from node
      where node.geo = EndPoint(link.geo) and
      (node.rowid in (
          select rowid from SpatialIndex where f_table_name = 'node' and
          search_frame = EndPoint(link.geo)) or
        node.node = new.node_b))
    where link.rowid = new.rowid;

    update link
    set "length" = round(ST_Length(new.geo), 8),
        "bearing_b" = round(Degrees(ST_Azimuth(ST_PointN(SanitizeGeometry(new.geo), ST_NumPoints(SanitizeGeometry(new.geo))-1), EndPoint(new.geo))),0),
        "bearing_a" =  round(Degrees(ST_Azimuth(StartPoint(geo), ST_PointN(SanitizeGeometry(geo), 2))),0)
    where link.rowid = new.rowid;

    -- now delete nodes which no-longer have attached links
    -- limit search to nodes which were attached to this link.
    delete from node
    where (node = old.node_a or node = old.node_b)
    --AND NOT (geo = EndPoint(new.geo) OR
    --         geo = StartPoint(new.geo))
    and node not in (
      select node_a
      from link
      where node_a is not null
      union all
      select node_b
      from link
      where node_b is not null);
  end;
--##

create trigger if not exists polaris_link_on_delete_record after delete on link
  begin
-- delete lonely node AFTER link deleted
    Delete from Node
    where node = old.node_a and
    node not in (SELECT node_a FROM link) and
    node not in (SELECT node_b FROM link);

    Delete from Node
    where node = old.node_b and
    node not in (SELECT node_a FROM link) and
    node not in (SELECT node_b FROM link);

    end;
--##

-- when you move a node, move attached links
create trigger if not exists polaris_node_on_geo_change after update of geo on node
  begin

    update link
    set geo = SetStartPoint(geo,new.geo)
    where node_a = new.node
    and StartPoint(geo) != new.geo;

    update link
    set geo = SetEndPoint(geo,new.geo)
    where node_b = new.node
    and EndPoint(geo) != new.geo;

    update node
    set "x" = round(ST_X(new.geo), 8),
        "y" = round(ST_Y(new.geo), 8),
        zone = (SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1)
    where node.rowid = new.rowid;

    update Transit_Walk
    set geo = SetStartPoint(geo,new.geo)
    where from_node = new.node
    and StartPoint(geo) != new.geo;

    update Transit_Walk
    set geo = SetEndPoint(geo,new.geo)
    where to_node = new.node
    and EndPoint(geo) != new.geo;

    update Transit_Bike
    set geo = SetStartPoint(geo,new.geo)
    where from_node = new.node
    and StartPoint(geo) != new.geo;

    update Transit_Bike
    set geo = SetEndPoint(geo,new.geo)
    where to_node = new.node
    and EndPoint(geo) != new.geo;

    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Node', 'geo');
  end;
--##
-- when you move a node on top of another node, steal all links FROM that node, AND delete it.
-- be careful of merging the node_as of attached links to the new node
-- this may be better as a TRIGGER ON link?

create trigger if not exists polaris_node_on_cannibalise_node before update of geo on node
  when
    -- detect another node in the new location
    (SELECT count(*)
    FROM node
    WHERE node != new.node
    AND geo = new.geo AND
    ROWID IN (
      SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
      search_frame = new.geo)) > 0
  BEGIN
    UPDATE link -- grab node_as belonging to node in same location
    SET node_a = new.node
    WHERE node_a = (SELECT node
                    FROM node
                    WHERE node != new.node
                    AND geo = new.geo AND
                    ROWID IN (
                      SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
                      search_frame = new.geo));
    UPDATE link -- grab node_bs belonging to node in same location
    SET node_b = new.node
    WHERE node_b = (SELECT node
                    FROM node
                    WHERE node != new.node
                    AND geo = new.geo AND
                    ROWID IN (
                      SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
                      search_frame = new.geo));
    -- delete nodes in same location
    DELETE FROM node
    WHERE node != new.node
    AND geo = new.geo AND
    ROWID IN (
      SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
      search_frame = new.geo);
  END;
--##
-- you may NOT CREATE a node on top of another node.
create trigger if not exists polaris_node_no_duplicate_node before insert on node
  when
    (SELECT count(*)
    FROM node
    WHERE node.node != new.node
    AND node.geo = new.geo AND
    node.ROWID IN (
      SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'node' AND
      search_frame = new.geo)) > 0
  BEGIN
    -- todo: change this to perform a cannibalisation instead.
    SELECT raise(ABORT, 'Cannot create on-top of other node');
  END;

--##

-- TODO: cannot CREATE node NOT attached.

-- don't delete a node, unless no attached links
create trigger if not exists polaris_node_dont_delete before delete on node
  when (SELECT count(*) FROM link WHERE node_a = old.node OR node_b = old.node) > 0
  BEGIN
    SELECT raise(ABORT, 'Node cannot be deleted, it still has attached link.');
  END;

--##
create trigger if not exists polaris_node_populates_fields_on_new_record after insert on node
begin
    update node
    set "x" = round(ST_X(new.geo), 8),
        "y" = round(ST_Y(new.geo), 8),
        zone = (SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1)
    where node.rowid = new.rowid;

    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Node', 'geo');
end;

--##
create trigger if not exists polaris_node_on_x_change after update of "x" on node
begin
    update node
    set "x" = round(ST_X(new.geo), 8)
    where node.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_node_on_y_change after update of "y" on node
begin
    update node
    set "y" = round(ST_Y(new.geo), 8)
    where node.rowid = new.rowid;
end;


--##
-- don't CREATE a node, unless on a link
-- CREATE BEFORE WHERE spatial index AND PointN()

-- when editing node, UPDATE connected links
-- This trigger is manually disabled and re-added in the network migration tool
create trigger if not exists polaris_node_on_node_change before update of node on node
  begin
--    select raise(ABORT, 'You cannot re-number a node.');
    -- The alternative below would only work if node were not the primary key
    update link set node_a = new.node
    where node_a = old.node;
    update link set node_b = new.node
    where node_b = old.node;
  end;

--##
create trigger if not exists polaris_node_on_node_change_after after update of node on node
  begin
    select RecoverSpatialIndex("Node", "geo");
  end;
