-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_link_overrides_new_override before insert on Link_Overrides
WHEN
    ((SELECT count(*) from (SELECT name FROM pragma_table_info('link')) where name=new.field)=0)
BEGIN
    SELECT raise(ABORT, 'Cannot add an override for a link field that does not exist');
end;

--##

create trigger if not exists polaris_link_overrides_change_field before update of field on Link_Overrides
WHEN
    ((SELECT count(*) from (SELECT name FROM pragma_table_info('link')) where name=new.field)=0)
BEGIN
    SELECT raise(ABORT, 'Cannot change an override to a link that does not exist');
end;

