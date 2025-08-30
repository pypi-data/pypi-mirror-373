-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ THIS TABLE IS NOT CURRENTLY BEING USED BY POLARIS
--@
--@

CREATE TABLE IF NOT EXISTS Use_Code(
    use_code             TEXT    NOT NULL PRIMARY KEY,
    rank                 INTEGER NOT NULL DEFAULT 0,
    routable             INTEGER NOT NULL DEFAULT 0,
    subset_of            TEXT             DEFAULT '',
    superset_of          TEXT             DEFAULT '',
    alternative_labels   TEXT             DEFAULT '',
    notes                TEXT             DEFAULT ''
);