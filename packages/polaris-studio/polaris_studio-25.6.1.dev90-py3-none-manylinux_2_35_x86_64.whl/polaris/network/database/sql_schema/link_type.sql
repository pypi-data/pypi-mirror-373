-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ This table collects all link types in the model with corresponding ranks,
--@ allowed vehicles and permission for the creation of turn pockets.
--@
--@ Turn pockets are only created if the values on *turn_pockets* are set to
--@ TRUE (not case-sensitive) OR if the field is not populated (default for
--@ older networks).
--@
--@ This flag does NOT, however, guarantee the creation of such pockets, as the
--@ need for them is only assessed during the creation of connections (see
--@ appropriate documentation for such)


create TABLE IF NOT EXISTS Link_Type(
    link_type             TEXT    NOT NULL PRIMARY KEY, --@ Name of the link type (e.g. Freeway, Principal, Collector, etc.)
    rank                  INTEGER NOT NULL DEFAULT 0,   --@ Rank of the link type. Lower rank implies higher hierarchy (e.g. Freeway = 10, Principal = 30, etc.)
    use_codes             TEXT    NOT NULL DEFAULT '',  --@ Modes allowed in the link, separated by a vertical bar
    turn_pocket_length    REAL    NOT NULL DEFAULT 50,  --@ Length of turn pockets, if allowed in meters
    turn_pockets          INTEGER NOT NULL DEFAULT 1,   --@ Flag to allow the creation of turn pockets. 1 = TRUE, 0 = FALSE
    minimum_speed         NUMERIC NOT NULL DEFAULT 0,   --@ Minimum speed limit for the link type in m/s
    speed_limit           NUMERIC NOT NULL DEFAULT 0,   --@ Maximum Speed limit for the link type in m/s
    alternative_labels    TEXT,                         --@ Alternative labels for the link type (e.g. Principal/Arterial)
    notes                 TEXT                          --@ user notes
);
