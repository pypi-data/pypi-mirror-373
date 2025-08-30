-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The parking table lists all parking facilities available in the model. It
--@ includes dedicated parking structures, as well as parking lots attached to
--@ business, residences and other activity locations.

create TABLE IF NOT EXISTS Parking(
    parking      INTEGER NOT NULL  NOT NULL PRIMARY KEY, --@ The parking facility identifier
    link         INTEGER NOT NULL,  --@ Foreign key reference to one link that is the closest spatially to the parking
    dir          INTEGER NOT NULL,  --@ The direction of the link (ab or ba) that is closest to the parking. Can be used to infer which side of the link this parking may lie (but not trivial)
    zone         INTEGER NOT NULL,  --@ The zone to which this parking facility belong
    offset       REAL,              --@ Auto-generated value of how far from the parking (perpendicular) the link is present (meters)
    setback      INTEGER,           --@ Auto-generated value of how far from node_a of the link this parking is present along the length of the link (meters)
    "type"       TEXT,              --@ The parking type: garage, lot, metered, street, etc.
    start        REAL,              --@ The offset of where segment begins (meters) (not currently used)
    end          REAL,              --@ The offset of where segment ends (meters) (not currently used)
    space        INTEGER NOT NULL,  --@ The capacity of this parking facility
    time_in      REAL,              --@ The start time from which this parking facility can be used
    time_out     REAL,              --@ The end time till which this parking facility can be used
    hourly       REAL    NOT NULL,  --@ The hourly parking rate ($)
    daily        REAL    NOT NULL,  --@ The daily parking rate ($)
    monthly      REAL,              --@ The monthly parking rate ($)
    walk_link    BIGINT,           --@ Foreign key reference to the nearest walk link from the Transit_Walk table
    walk_offset  REAL,              --@ Same as offset above, but for the walk link (meters)
    bike_link    BIGINT,           --@ Foreign key reference to the nearest bike link from the Transit_Bike table
    bike_offset  REAL,              --@ Same as offset above, but for the bike link (meters)

    CONSTRAINT "zone_fk" FOREIGN KEY("zone") REFERENCES "Zone"("zone") DEFERRABLE INITIALLY DEFERRED
);

select AddGeometryColumn( 'Parking', 'geo', SRID_PARAMETER, 'POINT', 'XY', 1);
select CreateSpatialIndex( 'Parking' , 'geo' );

create INDEX IF NOT EXISTS "parking_idx" ON "Parking" ("parking");
create INDEX IF NOT EXISTS "park_zone" ON "Parking" ("zone");
