-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

create trigger if not exists polaris_turn_overrides_rejects_on_new_record before insert on Turn_Overrides
  when (select count(link) from
            (Select link from link where link.node_a in (SELECT NODE_A node FROM LINK WHERE link=new.link and new.dir=1)
            union ALL
            Select link from link where link.node_b in (SELECT NODE_A node FROM LINK WHERE link=new.link and new.dir=1)
            union ALL
            Select link from link where link.node_a in (SELECT NODE_b node FROM LINK WHERE link=new.link and new.dir=0)
            union ALL
            Select link from link where link.node_b in (SELECT NODE_b node FROM LINK WHERE link=new.link and new.dir=0))
            where link=new.to_link)<1
  BEGIN
    SELECT raise(ABORT, 'Links are not connected');
end;

--##
create trigger if not exists polaris_turn_overrides_populates_fields_on_new_record after insert on Turn_Overrides
begin
    update Turn_Overrides
    set "node" = (SELECT CASE
                         WHEN new.dir =1 THEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.link)
                         ELSE (SELECT NODE_B FROM LINK WHERE LINK.link=new.link)
                         END as 'NODE')
    where Turn_Overrides.rowid = new.rowid;
    update Turn_Overrides
    set "to_dir" = (SELECT CASE
                         WHEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.to_link) = new.node THEN 0
                         ELSE 1
                         END as 'todir')
    where Turn_Overrides.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_turn_overrides_on_table_change after update on Turn_Overrides
begin
    update Turn_Overrides
    set "node" = (SELECT CASE
                         WHEN new.dir =1 THEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.link)
                         ELSE (SELECT NODE_B FROM LINK WHERE LINK.link=new.link)
                         END as 'NODE')
    where Turn_Overrides.rowid = new.rowid;
    update Turn_Overrides
    set "to_dir" = (SELECT CASE
                         WHEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.to_link) = new.node THEN 0
                         ELSE 1
                         END as 'todir')
    where Turn_Overrides.rowid = new.rowid;

end;

--##
create trigger if not exists polaris_turn_overrides_rejects_on_table_change before update on Turn_Overrides
  when (select count(link) from
            (Select link from link where link.node_a in (SELECT NODE_A node FROM LINK WHERE link=new.link and new.dir=1)
            union ALL
            Select link from link where link.node_b in (SELECT NODE_A node FROM LINK WHERE link=new.link and new.dir=1)
            union ALL
            Select link from link where link.node_a in (SELECT NODE_b node FROM LINK WHERE link=new.link and new.dir=0)
            union ALL
            Select link from link where link.node_b in (SELECT NODE_b node FROM LINK WHERE link=new.link and new.dir=0))
            where link=new.to_link)<1
  BEGIN
    SELECT raise(ABORT, 'Links are not connected');
end;