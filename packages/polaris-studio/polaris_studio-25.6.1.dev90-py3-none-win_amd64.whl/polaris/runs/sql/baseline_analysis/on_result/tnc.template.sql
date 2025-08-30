-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DROP TABLE IF EXISTS tnc_stats;
CREATE TABLE tnc_stats as
    SELECT  
        tnc_operator,
        avg(tot_pickups) as avg_trips_served,
        avg(charging_trips) as avg_charging_trips,
        avg(revenue) as avg_revenue,
        scaling_factor * sum(revenue) as total_revenue,
        scaling_factor * sum(trip_requests) as total_requests_offered_to_op

    FROM     TNC_Statistics
    GROUP BY 1;