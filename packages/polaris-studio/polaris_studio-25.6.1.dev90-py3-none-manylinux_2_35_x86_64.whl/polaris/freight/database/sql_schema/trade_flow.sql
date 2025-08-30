-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ An intput table for the trade flows between supplier and receiver
--@ pairs, including commodity type, annual demand in tonnage, type of trade,
--@ and external FAF zone if exists (for non internal-internal flows)

CREATE TABLE Trade_Flow (
    "trade_pair"      INTEGER NOT NULL PRIMARY KEY ,              --@ The unique identifier of this supplier-receiver pair
    "supplier"        INTEGER NOT NULL DEFAULT 0,                 --@ The supplier establishment identifier (foreign key to establishment table)
    "receiver"        INTEGER NOT NULL DEFAULT 0,                 --@ The receiver establishment identifier (foreign key to establishment table)
    "commodity"       INTEGER NOT NULL DEFAULT 0,                 --@ The commodity type being exchanged between this trade pair !COMMODITY_GROUP!
    "annual_demand"   REAL             DEFAULT 0,                 --@ Total annual traded tonnage (units: metric tons)
    "trade_type"      INTEGER NOT NULL DEFAULT 0,                 --@ Trade type (II, IE, EI, Import, Export) !TRADE_TYPE!
    "external_zone"   INTEGER          DEFAULT 0                  --@ External FAF Zone for trade types: IE, EI, Import, Export
);