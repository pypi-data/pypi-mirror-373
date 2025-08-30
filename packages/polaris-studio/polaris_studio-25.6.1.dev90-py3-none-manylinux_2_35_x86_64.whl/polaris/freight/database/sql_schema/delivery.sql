-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ An output table for the freight tours synthesized by CRISTAL,
--@ including their mode, volume, trip type,
--@ origin and destination

CREATE TABLE Delivery (
    "tour"                     INTEGER NOT NULL DEFAULT 0, --@ Freight tour identifier
    "leg"                      INTEGER NOT NULL DEFAULT 0, --@ Freight trip leg identifier within a tour
    "origin_location"          INTEGER NOT NULL DEFAULT 0, --@ The trip's origin location (foreign key to the Location table)
    "destination_location"     INTEGER NOT NULL DEFAULT 0, --@ The trip's destination location (foreign key to the Location table)
    "volume"                   NUMERIC NOT NULL DEFAULT 0, --@ Shipment volume (units: metric tons.)
    "is_e_commerce"            BOOLEAN NOT NULL DEFAULT 0, --@ boolean flag - is this an e-commerce delivery?
    "pickup_trip"              BOOLEAN NOT NULL DEFAULT 0, --@ boolean flag - is this a pick up trip?
    "off_hour_delivery"        INTEGER NOT NULL DEFAULT 0  --@ boolean flag - is this delivery performed in off hours?
);
