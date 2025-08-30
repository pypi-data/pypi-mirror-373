-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
create trigger if not exists polaris_network_updated_link before update of link on Link
  begin
    select raise(ABORT, 'You cannot re-number a link.');
  end;

--##

create trigger if not exists polaris_network_eliminates_ab_direction after update of lanes_ab on Link
  when
     (new.lanes_ab = 0 AND old.lanes_ab > 0)
  begin
    update link set
    cap_ab = 0,
    fspd_ab = 0
    where link.rowid = new.rowid;

    DELETE FROM Connection WHERE link=new.link AND "dir"=0;
    Delete from Pocket where link=old.link and dir = 0;
    Delete from Sign where link=old.link and dir = 0;
  end;

--##

create trigger if not exists polaris_network_eliminates_ba_direction after update of lanes_ba on Link
  when
     (new.lanes_ba = 0 AND old.lanes_ba > 0)
  begin
    update link set
    cap_ba = 0,
    fspd_ba = 0
    where link.rowid = new.rowid;

    Delete from Pocket where link=old.link and dir = 1;
    Delete from Sign where link=old.link and dir = 1;
    DELETE FROM Connection WHERE link=new.link AND "dir"=1;
  end;


--##
create trigger if not exists polaris_network_changes_ab_lanes after update of lanes_ab on Link
  when
     (new.lanes_ab > 0 AND old.lanes_ab = 0)
  begin
    -- This would trigger a rebuild of intersections, so we only do that if we change just a few things, and not all of them
    DELETE FROM Connection WHERE node=new.node_a;
    DELETE FROM Connection WHERE node=new.node_b;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Link', 'lanes');
  end;

--##
create trigger if not exists polaris_network_changes_ba_lanes after update of lanes_ba on Link
  when
     (new.lanes_ba > 0 AND old.lanes_ba = 0)
  begin
    DELETE FROM Connection WHERE node=new.node_a;
    DELETE FROM Connection WHERE node=new.node_b;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Link', 'lanes');
  end;

--##
create trigger if not exists polaris_network_fspd_ab_only_positive_for_available_direction after update of fspd_ab on Link
  when
     (new.lanes_ab = 0 and new.fspd_ab != 0)
  begin
        update Link set fspd_ab = 0 where ROWID=new.ROWID;
  end;

--##
create trigger if not exists polaris_network_fspd_ba_only_positive_for_available_direction after update of fspd_ba on Link
  when
     (new.lanes_ba = 0 and new.fspd_ba != 0)
  begin
    update Link set fspd_ba = 0 where ROWID=new.ROWID;
  end;

--##
create trigger if not exists polaris_network_cap_ab_only_positive_for_available_direction after update of cap_ab on Link
  when
     (new.lanes_ab = 0 and new.cap_ab != 0)
  begin
    update Link set cap_ab = 0 where ROWID=new.ROWID;
  end;

--##
create trigger if not exists polaris_network_cap_ba_only_positive_for_available_direction after update of cap_ba on Link
  when
     (new.lanes_ba = 0 and new.cap_ba != 0)
  begin
    update Link set cap_ba = 0 where ROWID=new.ROWID;
  end;

--##
create trigger if not exists polaris_network_preserves_fspd_ab_direction after update of fspd_ab on Link
  when
     (new.lanes_ab > 0 and new.fspd_ab <= 0)
  begin
    select raise(ROLLBACK, "You can't have zero fspd for positive number of lanes");
  end;

--##

create trigger if not exists polaris_network_preserves_fspd_ba_direction after update of fspd_ba on Link
  when
     (new.lanes_ba > 0 and new.fspd_ba <= 0)
  begin
    select raise(ROLLBACK, "You can't have zero fspd for positive number of lanes");
  end;

--##
create trigger if not exists polaris_link_queue_edit_delete_link after delete on Link
  begin
    Delete from Location_Links where link=old.link;
    Delete from Pocket where link=old.link;
    Delete from Sign where link=old.link;
    Delete from Connection where link=old.link or to_link=old.link;
    Delete from Turn_overrides where link=old.link or to_link=old.link;
    Delete from Transit_Walk where ref_link=old.link;
    Delete from Transit_Bike where ref_link=old.link;
    Delete from Toll_Pricing where  link = old.link;

    DELETE FROM Connection WHERE node=old.node_a;
    DELETE FROM Connection WHERE node=old.node_b;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Link', 'geo');
  end;

--##
create trigger if not exists polaris_link_queue_edit_add_link after INSERT on Link
  begin
    DELETE FROM Connection WHERE node=new.node_a;
    DELETE FROM Connection WHERE node=new.node_b;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Link', 'geo');
  end;

--##
create trigger if not exists polaris_link_queue_edit_change_geo_link after UPDATE of geo on Link
  begin
    DELETE FROM Connection WHERE node=new.node_a;
    DELETE FROM Connection WHERE node=new.node_b;
    DELETE FROM Connection WHERE node=old.node_a;
    DELETE FROM Connection WHERE node=old.node_b;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Link', 'geo');
  end;

--##
create trigger if not exists polaris_link_queue_edit_change_type_link after UPDATE of "type" on Link
  begin
    DELETE FROM Connection WHERE node=new.node_a;
    DELETE FROM Connection WHERE node=new.node_b;
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Link', 'type');
  end;


--##
create trigger if not exists polaris_node_queue_edit_delete after DELETE on Node
  begin
    Delete from Signal where nodes=old.node;
    DELETE FROM Road_Connectors where from_node = old.node;
    DELETE FROM Connection where node = old.node;
    DELETE FROM Sign where nodes = old.node;
  end;

--##
create trigger if not exists polaris_network_changes_on_zone_node after update of "zone" on node
begin
    update Node
        set
            zone = (SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1)
    where Node.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_network_changes_on_link_area_type after update of "area_type" on link
begin
    INSERT OR IGNORE INTO Geo_Consistency_Controller VALUES('Link', 'area_type');
end;

--##
create trigger if not exists polaris_network_update_link_toll_counterpart after update of "link" on Link
begin
    update Link set toll_counterpart = new.link where toll_counterpart=old.link;
end;

--##
create trigger if not exists polaris_network_prevent_delete_toll_counterpart before delete on Link
WHEN (SELECT count(*) FROM link WHERE toll_counterpart = old.link) > 0
BEGIN
  SELECT raise(ABORT, 'Node cannot delete a link that is the counterpart to a tolled facility');
END;

--##
create trigger if not exists polaris_network_delete_referring_records before delete on Link
WHEN (SELECT count(*) FROM link WHERE toll_counterpart = old.link) == 0
BEGIN
    DELETE FROM Connection WHERE link = old.link or to_link = old.link;
    DELETE FROM Link_Overrides WHERE link = old.link; -- In theory we don't need these, but the CASCADE DELETE may not work because of the freaking FKs being off
    DELETE FROM Location_Links WHERE link = old.link;
    DELETE FROM Pocket WHERE link = old.link;
    DELETE FROM Roadsideunit WHERE link = old.link;
    DELETE FROM Sign WHERE link = old.link;
    DELETE FROM Signal WHERE signal IN (SELECT signal FROM Phasing WHERE phasing_id IN (SELECT object_id FROM Phasing_Nested_Records WHERE value_link=old.link));
    DELETE FROM Toll_Pricing where  link = old.link;
    DELETE FROM Traffic_Incident where  link = old.link;
    DELETE FROM Transit_Pattern_Mapping where  link = old.link;
    DELETE FROM Transit_Walk where  ref_link = old.link;
    DELETE FROM Transit_Bike where  ref_link = old.link;
    DELETE FROM Turn_overrides where link=old.link or to_link=old.link;
END;

--##
-- Delete signals and connections after removing a node
create trigger if not exists polaris_cleans_up_after_removing_node after delete on node
  BEGIN
    DELETE FROM Connection WHERE node = old.node;
    DELETE FROM Sign WHERE nodes = old.node;
    DELETE FROM Signal WHERE nodes = old.node;
  END;
