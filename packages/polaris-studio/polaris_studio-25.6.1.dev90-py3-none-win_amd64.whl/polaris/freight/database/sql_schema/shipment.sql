-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ An output table for the freight shipment attributes,
--@ and mode choice results, including: the trade identifier,
--@ mode used, shipping cost, shipment size, shipment frequencies, 
--@ if the shipment use distribution center or no, and if that particular 
--@ shipment is simulated that day or no
--@

CREATE TABLE Shipment (
    "shipment"                          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, --@ The unique identifier of this shipment 
    "trade_pair"                        INTEGER NOT NULL DEFAULT 0,                 --@ The trade identifier from the trade flow table
    "mode"                              INTEGER NOT NULL DEFAULT 0,                 --@ The freight mode used for the shipment (truck, rail, air, courier) !FREIGHTMODE_TYPE!
    "total_cost"                        NUMERIC NOT NULL DEFAULT 0,                 --@ Total shipping cost of annual shipments (units: $USD)
    "shipment_size"                     NUMERIC NOT NULL DEFAULT 0,                 --@ Shipment size (units: metric tons)
    "order_interval"                    NUMERIC NOT NULL DEFAULT 0,                 --@ Time interval between two subsequent orders (units: days)
    "use_distribution"                  BOOLEAN NOT NULL DEFAULT 0,                 --@ boolean flag - is this shipment using a distribution center?
    "is_in_simulation_day"              BOOLEAN NOT NULL DEFAULT 0,                 --@ boolean flag - is the movement of this shipment simulated this day?
    "is_sampled"                        BOOLEAN NOT NULL DEFAULT 0,                 --@ boolean flag - is this shipment selected to be sampled?

    CONSTRAINT trade_pair_fk FOREIGN KEY (trade_pair)
    REFERENCES Trade_Flow (trade_pair) DEFERRABLE INITIALLY DEFERRED
);