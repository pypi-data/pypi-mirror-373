-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DROP TABLE IF EXISTS Mode_Distribution_ADULT;

CREATE TABLE IF NOT EXISTS mode_Distribution_ADULT AS
SELECT
    mode,
    scaling_factor * sum(trip.destination = person.work_location_id) AS 'HBW',
    scaling_factor * sum(trip.origin == household.location AND trip.destination <> person.work_location_id) AS 'HBO',
    scaling_factor * sum(trip.origin <> household.location AND trip.destination <> household.location AND trip.destination <> person.work_location_id) AS 'NHB',
    scaling_factor * count(*) AS total
FROM
    trip,
    person,
    household
WHERE
    trip.person = person.person
    AND person.household = household.household
    AND person.age > 16
    AND trip."end" - trip."start" > 2
GROUP BY
    mode;