# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import dataclasses
import logging
from enum import IntEnum
from os.path import join, dirname
from pathlib import Path
from sqlite3 import Connection, sqlite_version
from typing import List, Optional

import pandas as pd
from packaging import version

from polaris.network.starts_logging import logger
from polaris.network.utils.unzips_spatialite import jumpstart_spatialite
from polaris.utils.database.database_loader import GeoInfo
from polaris.utils.database.db_utils import commit_and_close, has_column, run_sql_file, has_table
from polaris.utils.database.spatialite_utils import spatialize_db
from polaris.utils.env_utils import is_windows
from polaris.utils.file_utils import readlines
from polaris.utils.list_utils import zero_or_one


class DatabaseType(IntEnum):
    Supply = 1
    Demand = 2
    Results = 3
    Freight = 4

    def __str__(self):
        return self.name

    @staticmethod
    def from_str(s):
        s = s.lower()
        if s == "supply":
            return DatabaseType.Supply
        if s == "demand":
            return DatabaseType.Demand
        if s == "results":
            return DatabaseType.Results
        if s == "freight":
            return DatabaseType.Freight
        raise ValueError(f"No such database type: {s}")


@dataclasses.dataclass
class StandardDatabase:
    base_directory: Path
    defaults_files: List[Path]

    @staticmethod
    def for_type(database_type):
        if database_type == DatabaseType.Supply:
            return StandardDatabase(Path(__file__).parent.parent.parent / "network" / "database")
        if database_type == DatabaseType.Demand:
            return StandardDatabase(Path(__file__).parent.parent.parent / "demand" / "database")
        if database_type == DatabaseType.Results:
            return StandardDatabase(Path(__file__).parent.parent.parent / "results" / "database")
        if database_type == DatabaseType.Freight:
            return StandardDatabase(Path(__file__).parent.parent.parent / "freight" / "database")
        raise RuntimeError(f"No standard database definition for {database_type}")

    def __init__(self, base_dir):
        self.base_directory = Path(base_dir)
        self.defaults_files = list(Path(base_dir).rglob("*.csv")) + list(Path(base_dir).rglob("*.zip"))
        self.geo_tables = self.tables(True, False)

    @property
    def sql_directory(self):
        return self.base_directory / "sql_schema"

    @property
    def default_values_directory(self):
        return self.base_directory / "default_values"

    def is_spatial_table(self, tablename):
        return tablename.lower() in [e.lower() for e in self.geo_tables]

    def tables(self, geotables=True, datatables=True):
        """Lists tables part of the STANDARD, and not the ones part of the current network

        Args:
            *geotables* (:obj:`bool`): If geo-enabled tables should be listed
            *datatables* (:obj:`bool`): If pure data tables should be listed
        """

        tables = []
        if geotables:
            tables += readlines(self.sql_directory / "geotables.txt")
        if datatables:
            tables += readlines(self.sql_directory / "datatables.txt")
            tables.append("migrations")

        return tables

    @staticmethod
    def ensure_required_tables(conn):
        if not has_table(conn, "Migrations"):
            run_sql_file(Path(join(dirname(__file__), "sql_schema", "migrations.sql")), conn)

    def add_table(self, conn: Connection, table_name: str, srid: Optional[int], add_defaults=True) -> None:
        # Create the table
        run_sql_file(self.sql_directory / f"{table_name.lower()}.sql", conn, {"SRID_PARAMETER": srid})

        if add_defaults:
            self.populate_table_with_defaults(conn, table_name)

        conn.commit()

    def populate_table_with_defaults(self, conn: Connection, table_name: str):
        """Populate a given table with default values (if they exists)"""

        # We look through all the files we have, ignoring case, to see if we have the one being added here.
        default_file = zero_or_one([e for e in self.defaults_files if e.stem.lower() == table_name.lower()])
        if default_file:
            table_name = default_file.stem  # get the correct case for the table
            existing_df = pd.read_sql(f"select * from {table_name}", conn)
            if existing_df.shape[0] > 0:
                logging.info(f"Replacing existing values in {table_name} with standard default set\n{existing_df}")
                conn.execute(f"DELETE FROM {table_name};")
            pd.read_csv(default_file).to_sql(table_name, conn, if_exists="append", index=False)

    def create_db(self, file, geo_info: GeoInfo, add_defaults=True, jumpstart=True):
        spatial = geo_info.is_geo_db
        if spatial and jumpstart:
            jumpstart_spatialite(file)

        with commit_and_close(file, missing_ok=True, spatial=spatial) as conn:
            spatial and spatialize_db(conn)
            self.create_tables(conn, geo_info, add_defaults)

    def create_tables(self, conn: Connection, geo_info: GeoInfo, add_defaults=True) -> None:

        logger.info("Creating Tables")
        spatial = geo_info.is_geo_db
        self.ensure_required_tables(conn)
        for table in [e for e in self.tables() if e.lower() != "migrations"]:
            logger.debug(f"     {table}")
            srid = geo_info.geo_info_for_table(table).srid if spatial else None  # type: ignore

            # For cases where we do have a list of srids, but not all tables are listed (could've been empty)
            srid = geo_info.get_most_frequent_srid() if spatial and srid is None else srid
            self.add_table(conn, table, srid, add_defaults)

    def drop_column(self, conn, table_name, column_name):
        self.drop_columns(conn, table_name, [column_name])

    def drop_columns(self, conn: Connection, table_name: str, column_names: List[str]):
        if not any(has_column(conn, table_name, col) for col in column_names):
            return
        if version.parse(sqlite_version) < version.parse("3.35"):
            self.drop_columns_legacy(conn, table_name, column_names)
        else:
            self.drop_columns_modern(conn, table_name, column_names)

    def drop_columns_modern(self, conn: Connection, table_name: str, column_names: List[str]):
        for col in column_names:
            conn.execute(f"ALTER TABLE {table_name} DROP COLUMN {col}")

    def drop_columns_legacy(self, conn: Connection, table_name: str, column_names: List[str]):
        # Thanks to poor support for "DROP COLUMN" in sqlite3 < 3.35 we do this horrible thing instead
        logging.error(f"Support for drop_columns requires sqlite3 version >= 3.35, found {sqlite_version}")
        script_name = "setup_windows_spatialite.py" if is_windows() else "setup_linux_sqlite.sh"
        logging.error(f"You can upgrade with  the script here: {script_name}")
        raise RuntimeError(f"Support for drop_columns requires sqlite3 version >= 3.35, found {sqlite_version}")
