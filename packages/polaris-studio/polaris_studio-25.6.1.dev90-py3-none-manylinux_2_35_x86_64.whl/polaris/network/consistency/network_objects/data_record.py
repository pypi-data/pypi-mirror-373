# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from typing import Union, Optional, Dict, Any

import pandas as pd
from shapely.geometry import Polygon, Point, LineString

from polaris.network.starts_logging import logger
from polaris.network.utils.srid import get_srid
from polaris.utils.database.data_table_access import DataTableAccess


class DataRecord:
    """General class to table elements into Python classes

    All geometries are transformed into Shapely geometries"""

    def __init__(
        self,
        element_id: int,
        table_name: str,
        data_storage: DataTableAccess,
        record: pd.DataFrame,
        conn: Optional[sqlite3.Connection] = None,
    ):
        self._data = data_storage
        self._table_name = table_name
        self.__original__: Dict[str, Any] = {}
        self.id = element_id
        self.__exists__ = True
        self.id = element_id
        self.geo: Union[Polygon, Point, LineString]
        self.__srid__ = get_srid(conn=conn, database_path=data_storage._database_file)
        self.type = ""

        if record.empty:
            data = self._data.get(table_name, conn)
            idx = self._data.table_index(table_name, conn)
            record = data[data[idx] == element_id]

        self._id_field = idx
        self.__dict__[self._id_field] = element_id
        if not record.empty:
            self.__original__[self._id_field] = element_id
            for col in record.columns:
                val = record[col].values[0]
                self.__dict__[col] = val
                self.__original__[col] = val
        else:
            self.__exists__ = False
            self.__original__[self._id_field] = None
            for col in record.columns:
                self.__dict__[col] = None
                self.__original__[col] = None
            self.id = element_id

    def save(self, conn: sqlite3.Connection):
        """Save this table record to the database"""
        if self.__exists__:
            to_change = []
            data = []
            qry = ""
            for key, val in self.__original__.items():
                if val != self.__dict__[key]:
                    if key == "geo":
                        to_change.append("geo=GeomFromWKB(?, ?)")
                        data.extend([self.geo.wkb, self.__srid__])
                    else:
                        to_change.append(f'"{key}"=?')
                        data.append(self.__dict__[key])
            if to_change:
                for key in self.__original__.keys():
                    self.__original__[key] = self.__dict__[key]
                qry = f'Update "{self._table_name}" set {",".join(to_change)} where "{self._id_field}"=?'
                data.append(self.id)
        else:
            self.__exists__ = True
            data = []
            keys = []
            string = []
            for key in self.__original__.keys():
                keys.append(f'"{key}"')
                if key == "geo":
                    data.extend([self.geo.wkb, self.__srid__])
                    string.append("GeomFromWKB(?,?)")
                else:
                    data.append(self.__dict__[key])
                    string.append("?")

            qry = f'INSERT into {self._table_name}({",".join(keys)}) VALUES({",".join(string)})'

        if data:
            try:
                conn.execute(qry, data)
                conn.commit()
            except Exception as e:
                logger.critical(qry)
                logger.critical(data)
                raise e

    def __setattr__(self, key, value):
        if value and key == "geo":
            self.__wkb__ = value.wkb
        self.__dict__[key] = value
