-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

DROP TABLE IF EXISTS Activity_Start_Distribution;
DROP TABLE IF EXISTS Activity_Start_Distribution_by_TOD;

CREATE TABLE Activity_Start_Distribution As
SELECT
    activity_stage_fn as activity_stage,
    cast(start_time/3600 as int) as start_time,
    scaling_factor * sum(CASE WHEN type='EAT OUT'         THEN 1 END) as EAT_OUT,
    scaling_factor * sum(CASE WHEN type='ERRANDS'         THEN 1 END) as ERRANDS,
    scaling_factor * sum(CASE WHEN type='HEALTHCARE'      THEN 1 END) as HEALTHCARE,
    scaling_factor * sum(CASE WHEN type='LEISURE'         THEN 1 END) as LEISURE,
    scaling_factor * sum(CASE WHEN type='PERSONAL'        THEN 1 END) as PERSONAL,
    scaling_factor * sum(CASE WHEN type='RELIGIOUS-CIVIC' THEN 1 END) as RELIGIOUS,
    scaling_factor * sum(CASE WHEN type='SERVICE'         THEN 1 END) as SERVICE,
    scaling_factor * sum(CASE WHEN type='SHOP-MAJOR'      THEN 1 END) as SHOP_MAJOR,
    scaling_factor * sum(CASE WHEN type='SHOP-OTHER'      THEN 1 END) as SHOP_OTHER,
    scaling_factor * sum(CASE WHEN type='SOCIAL'          THEN 1 END) as SOCIAL,
    scaling_factor * sum(CASE WHEN type='WORK'            THEN 1 END) as WORK,
    scaling_factor * sum(CASE WHEN type='PART_WORK'       THEN 1 END) as WORK_PART,
    scaling_factor * sum(CASE WHEN type='WORK AT HOME'    THEN 1 END) as WORK_HOME,
    scaling_factor * sum(CASE WHEN type='SCHOOL'          THEN 1 END) as SCHOOL,
    scaling_factor * sum(CASE WHEN type='PICKUP-DROPOFF'  THEN 1 END) as PICKUP,
    scaling_factor * sum(CASE WHEN type='HOME'            THEN 1 END) as HOME,
    scaling_factor * sum(1) AS total
FROM Activity a
WHERE (a.trip == 0 OR (a.Start_Time > 122 and a.trip <> 0))
  AND NOT (mode = 'NO_MOVE' and type in ('HOME','WORK AT HOME','PICKUP-DROPOFF'))
GROUP BY 1,2;


CREATE TABLE Activity_Start_Distribution_by_TOD as
SELECT
    time_of_day_fn as time_of_day,
    activity_stage,
    sum("EAT_OUT") as EAT_OUT,
    sum("ERRANDS") as ERRANDS,
    sum("HEALTHCARE") as HEALTHCARE,
    sum("LEISURE") as LEISURE,
    sum("PERSONAL") as PERSONAL,
    sum("RELIGIOUS") as RELIGIOUS,
    sum("SERVICE") as SERVICE,
    sum("SHOP_MAJOR") as SHOP_MAJOR,
    sum("SHOP_OTHER") as SHOP_OTHER,
    sum("SOCIAL") as SOCIAL,
    sum("WORK") as "WORK",
    sum("WORK_PART") as WORK_PART,
    sum("WORK_HOME") as WORK_HOME,
    sum("SCHOOL") as SCHOOL,
    sum("PICKUP") as PICKUP,
    sum("HOME") as HOME,
    sum("total") as Total
FROM
    "Activity_Start_Distribution"
group by
    1,2;
