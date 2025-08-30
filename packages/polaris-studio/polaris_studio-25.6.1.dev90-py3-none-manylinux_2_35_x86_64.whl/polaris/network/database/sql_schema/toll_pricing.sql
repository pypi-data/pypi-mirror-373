-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
CREATE TABLE IF NOT EXISTS Toll_Pricing(
    link            INTEGER NOT NULL,
    dir             INTEGER NOT NULL DEFAULT 0,
    start_time      INTEGER NOT NULL DEFAULT 0,
    end_time        INTEGER NOT NULL DEFAULT 0,
    price           REAL    NOT NULL DEFAULT 0,
    md_price        REAL    NOT NULL DEFAULT 0,
    hd_price        REAL    NOT NULL DEFAULT 0,

    CONSTRAINT "link_fk" FOREIGN KEY("link") REFERENCES "Link"("link") DEFERRABLE INITIALLY DEFERRED -- check
    CHECK("dir" >= 0),
    CHECK("dir" >= 0),
    CHECK("price" >= 0),
    CHECK(TYPEOF("dir") == 'integer')
);