# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3
import warnings
from importlib import util as iutil
from os import PathLike
from typing import Dict, Optional

import pandas as pd

from polaris.network.utils.srid import get_table_srid
from polaris.utils.database.db_utils import read_and_close
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.structure_finder import find_table_fields, find_table_index


class DataTableAccess:
    def __init__(self, database_file: PathLike):
        polaris_logging()
        self.__data_tables: Dict[str, pd.DataFrame] = {}
        self.__table_indices: Dict[str, pd.DataFrame] = {}
        self._database_file = database_file

    # def get_table(self, table_name: str, conn=None):  # type: ignore

    def get(self, table_name: str, conn=None, from_cache_ok=False):  # type: ignore
        """Returns a pandas dataframe for a project table. For geo-enabled tables, it returns a Pandas GeoDataFrame

        It always caches tables for repeated access by setting *from_cache_ok*=True.

        Args:
            *table_name* (:obj:`str`): Network table name
            *conn* `Optional` (:obj:`sqlite3.Connection`): Connection to the network database
            *from_cache_ok* `Optional` (:obj:`Bool`): Returns cached dataframe if available
        Return:
            *dataframe* (:obj:`pd.DataFrame`): Corresponding to the database
        """

        tn = table_name.lower()
        if tn not in self.__data_tables or not from_cache_ok:
            with conn or read_and_close(self._database_file, spatial=True) as connec:
                self.__data_tables[tn] = self.__build_layer(table_name, connec)

        return self.__data_tables[tn]

    def table_index(self, table_name: str, conn=None):
        if table_name not in self.__table_indices:
            with conn or read_and_close(self._database_file, spatial=True) as connec:
                self.__table_indices[table_name] = find_table_index(connec, table_name)
        return self.__table_indices[table_name]

    def get_table(self, table_name: str, conn: Optional[sqlite3.Connection] = None):
        warnings.warn("get_table() is deprecated. Use get() instead", DeprecationWarning, stacklevel=2)

        return self.get(table_name, conn)

    def plotting_layer(self, table_name: str, conn: Optional[sqlite3.Connection] = None):
        """Returns a pandas dataframe for a project table with geometry formatted as WKT for plotting.
        Layers are always projected to 4326 before they are returned

        Args:
            *table_name* (:obj:`str`): Network table name
            *conn* `Optional` (:obj:`sqlite3.Connection`): Connection to the network database
        Return:
            *dataframe* (:obj:`pd.DataFrame`): Corresponding to the database
        """
        warnings.warn("plotting_layer() is deprecated. Use get() instead", DeprecationWarning, stacklevel=2)
        return self.get(table_name, conn).to_crs(4326)

    def get_geo_layer(self, table_name: str, conn: Optional[sqlite3.Connection] = None):
        warnings.warn("get_geo_layer() is deprecated. Use get() instead", DeprecationWarning, stacklevel=2)
        return self.get(table_name, conn).to_crs(4326)

    def __build_layer(self, table_name: str, conn: sqlite3.Connection):
        with conn or read_and_close(self._database_file, spatial=True) as conn:
            fields, _, geo_field = find_table_fields(conn, table_name)
            if geo_field is not None and iutil.find_spec("geopandas") is None:
                logging.warning("Geopandas is not installed. Returning a Pandas DataFrame instead of a GeoDataFrame.")
            if geo_field is None or iutil.find_spec("geopandas") is None:
                return pd.read_sql(f"SELECT * FROM '{table_name}'", conn)
            return self.__geo_table_builder(table_name, conn, fields)

    def __geo_table_builder(self, table_name: str, conn: sqlite3.Connection, fields: list):
        import geopandas as gpd

        fields = [f'"{x}"' for x in fields]
        fields.append("Hex(ST_AsBinary(geo)) as geo")
        keys = ",".join(fields)
        sql = f"select {keys} from '{table_name}' WHERE geo IS NOT null;"
        return gpd.GeoDataFrame.from_postgis(sql, conn, geom_col="geo", crs=get_table_srid(conn, table_name))

    def refresh_cache(self, table_name="") -> None:
        """Refreshes a table in memory. Necessary when a table has been edited in disk

        Args:
           *table_name* (:obj:`str`) Name of the table to be refreshed in memory. Defaults to '', which refreshes
           all tables
        """
        if table_name == "":
            self.__data_tables.clear()
        else:
            _ = self.__data_tables.pop(table_name.lower(), None)
