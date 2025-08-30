-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table holds a list of database changes that have been made and that
--@ need to have consequences executed
--@ It replaces the old editing_table table and is used to track changes
--@ impossible (or impractical) to perform even with Spatialite's KNN2 triggers

CREATE TABLE IF NOT EXISTS Geo_Consistency_Controller(
    table_name      TEXT,    --@ The name of the table that was changed
    field_changed   TEXT,    --@ Name of the field that was altered.
    PRIMARY KEY (table_name, field_changed)
    );

create INDEX IF NOT EXISTS geo_consistency_controller_idx ON Geo_Consistency_Controller (table_name, field_changed);
create INDEX IF NOT EXISTS geo_consistency_controller_tname_idx ON Geo_Consistency_Controller (table_name);
create INDEX IF NOT EXISTS geo_consistency_controller_field_idx ON Geo_Consistency_Controller (field_changed);
