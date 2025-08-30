-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DELETE from Sign WHERE link in (select link from Link WHERE "type" IN ("FREEWAY", "EXPRESSWAY", "RAMP"));

UPDATE node SET control_type='';
UPDATE node SET control_type='stop_sign' WHERE node IN (SELECT nodes FROM Sign WHERE sign='STOP');
UPDATE node SET control_type='all_stop'  WHERE node IN (SELECT nodes FROM Sign WHERE sign='ALL_STOP');
UPDATE node SET control_type='signal'    WHERE node IN (SELECT nodes FROM Signal);
