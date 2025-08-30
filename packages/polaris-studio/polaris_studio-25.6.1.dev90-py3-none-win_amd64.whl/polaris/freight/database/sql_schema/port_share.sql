-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ An output table for the shipment leg that use airport and railport 
--@ This table is mainly used for analyzing and checking port share
--@

CREATE TABLE Port_Share (
    "port"           INTEGER NOT NULL,  --@ The identifier of the port
    "shipment"       INTEGER NOT NULL,  --@ The unique identifier of this shipment
    "leg"            INTEGER NOT NULL,  --@ The identifier of the internal trip leg for the shipment
    "weight"         NUMERIC NOT NULL,  --@ The shipment size of this shipment leg (units: metric tons)
    "mode"           INTEGER NOT NULL   --@ The freight mode used for this shipment leg !FREIGHTMODE_TYPE!

);
