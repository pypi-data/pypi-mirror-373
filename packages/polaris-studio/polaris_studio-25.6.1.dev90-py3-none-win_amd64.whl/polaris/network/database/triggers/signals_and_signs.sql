-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_signal_populates_fields_new_record after insert on Signal
begin
    update Signal
    set "times" = (SELECT count(*) from Signal_Nested_Records where object_id=new.signal)
    where Signal.rowid = new.rowid;
    update Node set "control_type" = "signal" where node=new.nodes;
    Delete from Sign where nodes=new.nodes;
end;

--##
create trigger if not exists polaris_signal_on_table_change after update on Signal
begin
    update Signal
    set "times" = (SELECT count(*) from Signal_Nested_Records where object_id=new.signal)
    where Signal.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_signal_on_delete_record after delete on Signal
begin
    Delete from Phasing where signal=old.signal;
    Delete from Timing where signal=old.signal;
    Delete from Signal_Nested_Records where object_id= old.signal;
    update Node set "control_type" = "" where node=old.nodes;
end;


--##
create trigger if not exists polaris_signal_nested_records_populates_fields_new_record after insert on Signal_Nested_Records
begin
    update Signal
    set "times" = (SELECT count(*) from Signal_Nested_Records where object_id=new.object_id)
    where Signal.signal = new.object_id;
end;

--##
create trigger if not exists polaris_signal_nested_records_on_table_change after update on Signal_Nested_Records
begin
    update Signal
    set "times" = (SELECT count(*) from Signal_Nested_Records where object_id=new.object_id)
    where Signal.signal in (new.object_id, old.object_id);
end;

--##
create trigger if not exists polaris_signal_nested_records_on_delete_record after delete on Signal_Nested_Records
begin
    update Signal
    set "times" = (SELECT count(*) from Signal_Nested_Records where object_id=old.object_id)
    where Signal.signal = old.object_id;
end;


--##
create trigger if not exists polaris_phasing_nested_records_populates_fields_new_record after insert on Phasing_Nested_Records
begin
    update Phasing
    set "movements" = (SELECT count(*) from Phasing_Nested_Records where object_id=new.object_id)
    where Phasing.phasing_id = new.object_id;
end;

--##
create trigger if not exists polaris_phasing_nested_records_on_table_change after update on Phasing_Nested_Records
begin
    update Phasing
    set "movements" = (SELECT count(*) from Phasing_Nested_Records where object_id=new.object_id)
    where Phasing.phasing_id in (new.object_id, old.object_id);
end;

--##
create trigger if not exists polaris_phasing_nested_records_on_delete_record after delete on Phasing_Nested_Records
begin
    update Phasing
    set "movements" = (SELECT count(*) from Phasing_Nested_Records where object_id=old.object_id)
    where Phasing.phasing_id = old.object_id;
end;


--##

create trigger if not exists polaris_phasing_on_delete_record after delete on Phasing
begin
    Delete from Phasing_Nested_Records where object_id=old.phasing_id;
end;

--##
create trigger if not exists polaris_phasing_populates_fields_new_record after insert on Phasing
begin
    update Phasing
    set "movements" = (SELECT count(*) from Phasing_Nested_Records where object_id=new.phasing_id)
    where Phasing.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_phasing_on_table_change after update on Phasing
begin
    update Phasing
    set "movements" = (SELECT count(*) from Phasing_Nested_Records where object_id=new.phasing_id)
    where Phasing.rowid in (new.rowid, old.rowid);
end;



--##
create trigger if not exists polaris_timing_nested_records_populates_fields_new_record after insert on Timing_Nested_Records
begin
    update Timing
    set "cycle" = coalesce((select sum(value_maximum) + sum(value_red)+ sum(value_yellow) from Timing_Nested_Records where object_id=new.object_id),0),
    "phases" = coalesce((SELECT count(*) from Timing_Nested_Records where object_id=new.object_id),0)
    where Timing.timing_id = new.object_id;
end;

--##
create trigger if not exists polaris_timing_nested_records_on_table_change after update on Timing_Nested_Records
begin
    update Timing
    set "cycle" = coalesce((select sum(value_maximum) + sum(value_red)+ sum(value_yellow) from Timing_Nested_Records where object_id=new.object_id),0),
    "phases" = coalesce((SELECT count(*) from Timing_Nested_Records where object_id=new.object_id),0)
    where Timing.timing_id in (new.object_id, old.object_id);
end;

--##
create trigger if not exists polaris_timing_nested_records_on_delete_record after delete on Timing_Nested_Records
begin
    update Timing
    set "cycle" = coalesce((select sum(value_maximum) + sum(value_red)+ sum(value_yellow) from Timing_Nested_Records where object_id=old.object_id),0),
    "phases" = coalesce((SELECT count(*) from Timing_Nested_Records where object_id=old.object_id),0)
    where Timing.timing_id = old.object_id;
end;

--##
create trigger if not exists polaris_timing_on_delete_record after delete on Timing
begin
    Delete from Timing_Nested_Records where object_id=old.timing_id;
end;

--##
create trigger if not exists polaris_timing_on_table_change after update on Timing
begin
    update Timing
    set "cycle" = coalesce((select sum(value_maximum) + sum(value_red)+ sum(value_yellow) from Timing_Nested_Records where object_id=new.timing_id),0),
    "phases" = coalesce((SELECT count(*) from Timing_Nested_Records where object_id=new.timing_id),0)
    where Timing.timing_id in (new.timing_id, old.timing_id);

end;

--##
create trigger if not exists polaris_timing_populates_fields_new_record after insert on Timing
begin
    update Timing
    set "cycle" = coalesce((select sum(value_maximum) + sum(value_red)+ sum(value_yellow) from Timing_Nested_Records where object_id=new.timing_id),0),
    "phases" = coalesce((SELECT count(*) from Timing_Nested_Records where object_id=new.timing_id),0)
    where Timing.timing_id = new.timing_id;
end;

--##
create trigger if not exists polaris_sign_populates_fields_new_record after insert on Sign
begin
    update Sign
    set "nodes" = (SELECT CASE
                         WHEN dir =1 THEN (SELECT NODE_A FROM LINK WHERE LINK.link=new.link)
                         ELSE (SELECT NODE_B FROM LINK WHERE LINK.link=new.link)
                         END as 'NODE')
    where Sign.rowid = new.rowid;
    update Node set "control_type" = (select case when new.sign='ALL_STOP' then 'all_stop' else 'stop_sign' end)
    where node=new.nodes;
    Delete from Signal where nodes=new.nodes;
end;

--##
create trigger if not exists polaris_sign_no_stop_on_freeway before insert on Sign
when
    (select count(*) from link where link=new.link and "type" IN ("FREEWAY", "EXPRESSWAY", "RAMP"))>0
begin
    select raise(ROLLBACK, "You canot add a stop sign on a freeway, expressway or ramp");
end;

--##
create trigger if not exists polaris_sign_on_delete_record after delete on Sign
begin
    UPDATE Node SET control_type = '' WHERE node=old.nodes;
end;