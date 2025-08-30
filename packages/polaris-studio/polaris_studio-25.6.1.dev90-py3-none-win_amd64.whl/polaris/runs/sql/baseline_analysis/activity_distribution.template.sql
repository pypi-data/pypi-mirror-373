-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DROP TABLE IF EXISTS person_distribution;
CREATE TABLE IF NOT EXISTS person_distribution AS
SELECT person_type_fn AS pertype, CAST(COUNT(*) as real) AS total
FROM person p
GROUP BY pertype;

DROP TABLE IF EXISTS activity_distribution;
CREATE TABLE IF NOT EXISTS activity_distribution AS
SELECT person_type_fn AS pertype,
       activity_type_fn as acttype,
       activity_stage_fn as activity_stage,
       cast(count(*) as real) as count
FROM person p, activity a
WHERE p.person = a.person
AND not (a.mode == 'NO_MOVE' AND a.type in ('HOME','WORK AT HOME','PICKUP-DROPOFF'))
AND (a.trip == 0 OR (a.Start_Time > 122 AND a.trip <> 0))
GROUP BY 1,2,3;

DROP TABLE IF EXISTS activity_rate_distribution;
CREATE TABLE activity_rate_distribution AS
SELECT ad.pertype AS pertype, ad.acttype AS acttype, ad.activity_stage, ad.count/pd.total AS rate, 
       pd.total as person_count, ad.count as activity_count
FROM activity_distribution ad, person_distribution pd
WHERE ad.pertype = pd.pertype
ORDER BY pertype, acttype;
