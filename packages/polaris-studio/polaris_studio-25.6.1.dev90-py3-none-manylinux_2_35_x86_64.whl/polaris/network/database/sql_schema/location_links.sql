-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table lists all the links to which each location would have direct
--@ access to. The basic idea is that loading all trips to/from a location only
--@ to the closest link to it would create an artificially high level of
--@ congestion in a model with a simplified network.
--@
--@ Two algorithms are available for the creation of this table: all links
--@ that allow autos and pedestrians and that form the "box that encircles the location",
--@ where one is the closest of all links and the others are the
--@ closest in directions rotated 90 degrees, starting from the vector that connects the
--@ connection and the closest link. When only one or two links are found, polaris-studio tries the intermediary
--@ angles every 45 degrees in search for links that had not been found
--@ The second algorithm simply connects the location to the closest link that allows autos.

create TABLE IF NOT EXISTS Location_Links(
    location    INTEGER NOT NULL, --@ Foreign key reference to the location this entry refers to
    link        INTEGER NOT NULL, --@ Foreign key reference to the link this entry refers to
    distance    REAL,             --@ Straight line distance (in meters) from the location to the link
    
    CONSTRAINT "location_fk" FOREIGN KEY("location") REFERENCES "location"("location") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "link"("link") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);


create INDEX IF NOT EXISTS "Location_Links_location" ON "Location_Links" ("location");
create INDEX IF NOT EXISTS "Location_Links-link" ON "Location_Links" ("link");
CREATE UNIQUE INDEX IF NOT EXISTS "Location_Links_unique" ON "Location_Links" (location, link);