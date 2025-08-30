-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table lists the corresponding parking facility for each location (when
--@  available) and the distance to it

-- TODO: Field id does not seem to be used
create TABLE IF NOT EXISTS Location_Parking(
    location INTEGER NOT NULL, --@ Foreign key reference to the location this entry refers to
    parking  INTEGER NOT NULL, --@ Foreign key reference to the parking facility this entry refers to
    distance REAL,             --@ The straight line distance (in meters) between this pair of parking and location
    id       INTEGER,          --@ The unique identifier of this entry
    
    CONSTRAINT "location_fk" FOREIGN KEY("location") REFERENCES "location"("location") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "parking_fk" FOREIGN KEY("parking") REFERENCES "parking"("parking") DEFERRABLE INITIALLY DEFERRED
);

create INDEX IF NOT EXISTS "loc_parking_idx" ON "Location_Parking" ("location");