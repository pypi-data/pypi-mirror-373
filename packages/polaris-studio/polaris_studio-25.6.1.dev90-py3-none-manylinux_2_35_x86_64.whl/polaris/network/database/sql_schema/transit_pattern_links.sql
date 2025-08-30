-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Transit_Pattern_Links table holds the information on the sequence of
--@ of transit links that are traversed by each transit pattern
--@

CREATE TABLE IF NOT EXISTS Transit_Pattern_Links(
    pattern_id     BIGINT     NOT NULL, --@ ID of the pattern in the format AARRRRPPPP0000 (Agency, Route, Pattern)
    "index"        INTEGER    NOT NULL, --@ Sequence number of the link served by the pattern
    transit_link   BIGINT     NOT NULL, --@ ID of the transit link that the pattern serves at the given "index" sequence

    FOREIGN KEY(pattern_id) REFERENCES "Transit_Patterns"(pattern_id) deferrable initially deferred,
    FOREIGN KEY(transit_link) REFERENCES "Transit_Links"(transit_link) deferrable initially deferred
);

create UNIQUE INDEX IF NOT EXISTS transit_pattern_links_stop_id ON Transit_Pattern_Links (pattern_id, transit_link);
