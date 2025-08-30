-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

DROP TABLE IF EXISTS activity_summary;
CREATE TABLE activity_summary AS
SELECT a."type"                 AS activity_type,
       income_quintile_fn       AS income_quintile,
       race_fn                  AS race,
       gender_fn                AS gender,
       l1."zone"                AS household_zone,
       l2."zone"                AS activity_zone,
       scaling_factor * count() AS activity_count
FROM activity a, person p, household, a.location l1, a.location l2
WHERE a.start_time > 122
  AND a.trip > 0
  AND a.person = p.person
  AND p.household = household.household
  AND l1.location = household.location
  AND l2.location = a.location_id
GROUP BY activity_type, income_quintile, race, gender, household_zone, activity_zone;