-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Location table holds all the activity and household locations in the
--@ model, on which all trips will ultimately start and end.
--@
--@ Given its central importance in the model, this table is connected to
--@ multiple other tables, both through data links and geographic ones.
--@
--@ Required by all models.

create TABLE IF NOT EXISTS Location(
    location         INTEGER NOT NULL PRIMARY KEY,    --@ Unique ID referencing a particular location in the model
    link             INTEGER NOT NULL,                --@ Foreign key reference to one link that is the closest spatially to the location
    dir              INTEGER NOT NULL DEFAULT 0,      --@ The direction of the link (ab or ba) that is closest to the location. Can be used to infer which side of the link this location may lie (but not trivial).
    offset           REAL    NOT NULL DEFAULT 0,      --@ Auto-generated value of how far from the location (perpendicular) the link is present.
    setback          REAL    NOT NULL DEFAULT 0,      --@ Auto-generated value of how far from node_a of the link this location is present along the length of the link
    "zone"           INTEGER,                         --@ Foreign key reference to the zone where this location in situated. Auto-generated through geo-consistency checks.
    x                REAL    NOT NULL DEFAULT 0,      --@ Auto-generated value of the x coordinate of the location specified in meters (UTM transform)
    y                REAL    NOT NULL DEFAULT 0,      --@ Auto-generated value of the y coordinate of the location specified in meters (UTM transform)
    area_type        INTEGER NOT NULL DEFAULT 0,      --@ Foreign-key reference to Area_Type to define the general characteristic of the area where the location is situated. It is necessarily the same as the zone where the location is situated
    lu_area          REAL    NOT NULL DEFAULT 0,      --@ The area (in ???) of the same land use aggregated around the location
    notes            TEXT             DEFAULT "",     --@ Text area to specify notes about the location. Optional.
    popsyn_region    BIGINT  NOT NULL DEFAULT 0,      --@ Foreign key reference to the PopSyn_Region table denoting the collection of locations considered during population synthesis.
    county           BIGINT                    ,      --@ County code for the location. Used by the freight model and to compute aggregate statistics
    land_use         TEXT    NOT NULL DEFAULT "ALL",  --@ Text describing the land use type represented by this location. !LAND_USE!
    walk_link        BIGINT,                          --@ Foreign key reference to the nearest walk link from the Transit_Walk table
    walk_offset      REAL,                            --@ Same as offset above, but for the walk link.
    bike_link        BIGINT,                          --@ Foreign key reference to the nearest bike link from the Transit_Bike table
    bike_offset      REAL,                            --@ Same as offset above, but for the bike link.
    avg_parking_cost REAL             DEFAULT 0,      --@ Average parking cost when visiting the location. Used in the activity planning stage.
    res_charging     REAL,                            --@ Denotes the proportion of households at this location that have residential charging available.
    stop_flag        INTEGER          DEFAULT 0,      --@ Boolean to denote whether or not a location is a TNC stop, primarily for aggregated pickups and drop-offs. May be deprecated.
    tod_distance     REAL    NOT NULL DEFAULT 0,      --@ Walk distance to the closest high-quality transit stop, in meters. The definition of "high quality" is user dependent and can be calculated using the DistanceToTransit class from Polaris-Studio.

    CONSTRAINT "land_use_fk" FOREIGN KEY("land_use") REFERENCES "Land_Use"("land_use") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "county_fk" FOREIGN KEY("county") REFERENCES "Counties"("county") DEFERRABLE INITIALLY DEFERRED
);

select AddGeometryColumn( 'Location', 'geo', SRID_PARAMETER, 'POINT', 'XY', 1 );
select CreateSpatialIndex( 'Location' , 'geo');

create INDEX IF NOT EXISTS "notes_idx" ON "Location" ("notes");
create INDEX IF NOT EXISTS "loc_zone" ON "Location" ("zone");
create INDEX IF NOT EXISTS "location_idx" ON "Location" ("location");

