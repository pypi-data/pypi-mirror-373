# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

from polaris.network.utils.unzips_spatialite import jumpstart_spatialite
from polaris.utils.database.db_utils import commit_and_close


def start_cache(db_filename: Path) -> None:
    if not db_filename.exists():
        jumpstart_spatialite(db_filename)
    with commit_and_close(db_filename, spatial=True) as conn:
        table_sql = [
            """CREATE TABLE IF NOT EXISTS osm_elements(
                                                     osm_id         INTEGER NOT NULL PRIMARY KEY,
                                                     x              REAL,
                                                     y              REAL,
                                                     tag            TEXT,
                                                     tag_value      TEXT,
                                                     all_tags       TEXT,
                                                     download_id    TEXT
         );""",
            "select AddGeometryColumn( 'osm_elements', 'geo', 4326, 'POINT', 'XY', 1);",
            "select CreateSpatialIndex( 'osm_elements' , 'geo' );",
        ]

        downloads_sql = [
            """CREATE TABLE IF NOT EXISTS osm_downloads(
                                                     id             TEXT PRIMARY KEY,
                                                     download_date  TEXT,
                                                     tag            TEXT,
                                                     tag_value      TEXT
            );""",
            "select AddGeometryColumn( 'osm_downloads', 'geo', 4326, 'POLYGON', 'XY', 1);",
            "select CreateSpatialIndex( 'osm_downloads' , 'geo' );",
        ]
        for sql in table_sql + downloads_sql:
            conn.execute(sql)
