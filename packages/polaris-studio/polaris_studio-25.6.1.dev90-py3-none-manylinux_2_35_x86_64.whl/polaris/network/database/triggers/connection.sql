-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_connection_populates_fields_on_new_record after insert on Connection
begin
    update Connection
    set "node" = (SELECT CASE
                         WHEN dir =1 THEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.link)
                         ELSE (SELECT NODE_B FROM LINK WHERE LINK.link=new.link)
                         END as 'NODE')
    where Connection.rowid = new.rowid;
    update Connection
    set "to_dir" = (SELECT CASE
                         WHEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.to_link) = new.node THEN 0
                         ELSE 1
                         END as 'todir')
    where Connection.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_connection_on_table_change after update on Connection
begin
    update Connection
    set "node" = (SELECT CASE
                         WHEN dir =1 THEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.link)
                         ELSE (SELECT NODE_B FROM LINK WHERE LINK.link=new.link)
                         END as 'NODE')
    where Connection.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_connection_on_node_change after update of node on Connection
begin
    update Connection
    set "to_dir" = (SELECT CASE
                         WHEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.to_link) = new.node THEN 0
                         ELSE 1
                         END as 'todir')
    where Connection.rowid = new.rowid;
end;