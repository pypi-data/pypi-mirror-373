-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table holds metadata about the model, and it has become a requirement
--@ since the introduction of this formal data model for the Polaris network.
--@
--@ This table holds the information on the data model version this network is
--@ compatible with, and therefore crucial to not be manually edited by the user
--@
--@ The hand of driving field determines on which side of the road cars should drive.

CREATE TABLE IF NOT EXISTS About_Model(
    infoname    TEXT NOT NULL PRIMARY KEY,    --@ The key used to look up metadata (i.e. "build-date")
    infovalue   TEXT NOT NULL DEFAULT ''      --@ The value (actual data) (i.e. "2024-01-24")
);