-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ For each transit trip, this table lists the arrival and departure at each
--@ stop, listed in order by their index in the sequence available in
--@ the transit pattern links table
--@
--@ The transit trip ID can be traced back to the pattern, route and agency
--@ directly through the encoding of their trip_id, as explained in the
--@ documentation for the Transit_Agencies table.
--@
--
--@ The time_source field indicates whether the stop timing came from the GTFS
--@ feed (**0**) or from any pre-processing (i.e. stop_time_de-duplication) (**1**).

CREATE TABLE IF NOT EXISTS Transit_Trips_Schedule(
    trip_id      BIGINT   NOT NULL,           --@ ID of the trip as seen in the transit_trips table
    "index"      INTEGER  NOT NULL,           --@ Sequence number of the stop served by the pattern
    arrival      INTEGER  NOT NULL,           --@ Vehicle arrival time at the stop in seconds from the beginning of the day
    departure    INTEGER  NOT NULL,           --@ Vehicle departure time from the stop in seconds from the beginning of the day
    time_source  INTEGER  NOT NULL DEFAULT 0, --@ 0 indicates that the times in GTFS were used directly, 1 indicates that corrections were made

    PRIMARY KEY(trip_id,"index"),
    FOREIGN KEY(trip_id) REFERENCES Transit_Trips(trip_id) deferrable initially deferred
);
