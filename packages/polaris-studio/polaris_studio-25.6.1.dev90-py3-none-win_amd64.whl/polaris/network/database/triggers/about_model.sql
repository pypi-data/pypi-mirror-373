-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--##
create trigger if not exists polaris_about_model_prevent_delete_version before delete on About_Model
when
old.infoname in ("hand_of_driving")
begin
    select raise(ROLLBACK, "You cannot delete this record");
end;
