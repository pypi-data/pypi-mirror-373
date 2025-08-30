-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all traffic analysis zones (TAZs) in the model, along with socio-economic data
--@ associated to each zone. 
--@ 
--@ Forms the building block and is typicaly the first layer created for a new model.
--@
--@ Required by all models.

CREATE TABLE IF NOT EXISTS Zone (
    zone                       INTEGER NOT NULL              PRIMARY KEY, --@ Zone ID
    x                          REAL    NOT NULL    DEFAULT 0,   --@ X coordinate of the zone centroid. Automatically added by Polaris.
    y                          REAL    NOT NULL    DEFAULT 0,   --@ Y coordinate of the zone centroid. Automatically added by Polaris.
    z                          REAL,                            --@ Not currently in use
    area_type                  INTEGER NOT NULL    DEFAULT 100, --@ Area type of the zone. Default is 0.
    area                       REAL    NOT NULL    DEFAULT 0,   --@ Area of the zone in square meters. Automatically created
    entertainment_area         REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    industrial_area            REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    institutional_area         REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    mixed_use_area             REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    office_area                REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    other_area                 REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    residential_area           REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    retail_area                REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    school_area                REAL    NOT NULL    DEFAULT 0,   --@ Land use specific area in square meters for use in destination choice. Automatically created. Optional.
    pop_households             INTEGER NOT NULL    DEFAULT 0,   --@ Number of households present in the TAZ. Used in population synthesis as a target for the TAZ.  Mandotory for model run.
    pop_persons                INTEGER NOT NULL    DEFAULT 0,   --@ Number of people living in the TAZ. Used in population synthesis as a target for the TAZ.  Mandotory for model run.
    pop_group_quarters         INTEGER NOT NULL    DEFAULT 0,   --@ Number of people living in a group quarters setting in the TAZ. Used in the population synthesis as a target for the TAZ.  Mandotory for model run.
    employment_total           INTEGER NOT NULL    DEFAULT 0,   --@ Total number of jobs across all types available in the zone. Mandotory for model run.
    employment_retail          INTEGER NOT NULL    DEFAULT 0,   --@ Number of jobs of specific type in the TAZ. Used with destination choice.
    employment_government      INTEGER NOT NULL    DEFAULT 0,   --@ Number of jobs of specific type in the TAZ. Used with destination choice.
    employment_manufacturing   INTEGER NOT NULL    DEFAULT 0,   --@ Number of jobs of specific type in the TAZ. Used with destination choice.
    employment_services        INTEGER NOT NULL    DEFAULT 0,   --@ Number of jobs of specific type in the TAZ. Used with destination choice.
    employment_industrial      INTEGER NOT NULL    DEFAULT 0,   --@ Number of jobs of specific type in the TAZ. Used with destination choice.
    employment_other           INTEGER NOT NULL    DEFAULT 0,   --@ Number of jobs of specific type in the TAZ. Used with destination choice.
    percent_white              REAL    NOT NULL    DEFAULT 0,   --@ Percent of population within TAZ that is Caucasian. Not used except if needed in choice models.
    percent_black              REAL    NOT NULL    DEFAULT 0,   --@ Percent of population within TAZ that is African-American. Not used except if needed in choice models.
    hh_inc_avg                 REAL    NOT NULL    DEFAULT 0,   --@ Average household income of all households within the TAZ. Not used except if needed in choice models.
    electric_grid_transmission INTEGER NOT NULL DEFAULT 1,      --@ Foreign key reference to the Electricity_Grid_Transmission table to determine which transmission bus the zone falls under.
    electricity_provider       INTEGER NOT NULL   DEFAULT 1,    --@ Foreign key reference to the Electricity_Provider table to determine which utility covers the zone.

    FOREIGN KEY("area_type") REFERENCES "Area_Type"("area_type") deferrable initially deferred,
    FOREIGN KEY("electric_grid_transmission") REFERENCES "Electricity_Grid_Transmission"("Transmission_Bus_ID") deferrable initially deferred,
    FOREIGN KEY("electricity_provider") REFERENCES "Electricity_Provider"("Provider_ID") deferrable initially deferred
);

SELECT AddGeometryColumn( 'Zone', 'geo', SRID_PARAMETER, 'MULTIPOLYGON', 'XY' );
SELECT CreateSpatialIndex( 'Zone' , 'geo' );

CREATE INDEX IF NOT EXISTS "IDX_ZONE_AREA" ON "Zone" ("area_type");
