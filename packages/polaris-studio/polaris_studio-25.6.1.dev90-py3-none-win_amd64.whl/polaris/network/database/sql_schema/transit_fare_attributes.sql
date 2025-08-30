-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ All transit fares for transit agencies in the model are included on this
--@ table. It includes the agency ID is applies to, as well as price and
--@ transfer criteria, which are crucial for proper consideration for trip
--@ routing.


create TABLE IF NOT EXISTS Transit_Fare_Attributes (
    fare_id           INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ ID of the trip in the format AA000000000000 (Agency)
    fare              TEXT    NOT NULL, --@ ID of the fare as contained on GTFS
    agency_id         INTEGER NOT NULL, --@ ID of the agency to which the fare applies
    price             REAL,             --@ Fare in dollars
    currency          TEXT,             --@ Currency of the fare as shown on GTFS
    payment_method    INTEGER,          --@ Indicates when the fare must be paid as shown in GTFS, not currently used in POLARIS
    transfer          INTEGER,          --@ Indicates the number of transfers permitted on this fare as shown in GTFS. Empty implies unlimited transfers
    transfer_duration REAL,             --@ Length of time in seconds before a transfer expires as shown in GTFS.

    FOREIGN KEY(agency_id) REFERENCES Transit_Agencies(agency_id) deferrable initially deferred
);

CREATE UNIQUE INDEX IF NOT EXISTS fare_transfer_uniqueness ON Transit_Fare_Attributes (fare_id, transfer);