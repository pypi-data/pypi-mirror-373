# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import dataclasses
import glob
import os
from io import StringIO
from os.path import join, exists
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from pandas import DataFrame
from polaris.network.starts_logging import logger
from polaris.network.utils.clean_sql_type import clean_sql_type
from polaris.network.utils.geotypes import spatialite_types
from polaris.utils.database.database_dumper import EXCL_NAME_PAT
from polaris.utils.database.db_utils import list_tables_in_db, commit_and_close
from polaris.utils.database.sqlite_types_afinity import sql_to_numpy
from polaris.utils.file_utils import df_from_file
from polaris.utils.signals import SIGNAL


@dataclasses.dataclass
class TableGeoInfo:
    srid: int
    geo_column: str
    geo_type: int


@dataclasses.dataclass
class GeoInfo:
    is_geo_db: bool
    srids: pd.DataFrame
    geo_tables: List[str]
    fixed_srid: Optional[int]

    @staticmethod
    def from_folder(folder_name):
        srid_file = join(folder_name, "srids.csv")
        if not exists(srid_file):
            return GeoInfo(False, pd.DataFrame([]), [], None)

        srids = pd.read_csv(srid_file)
        geo_tables = srids.table_name.tolist()
        return GeoInfo(True, srids, geo_tables, None)

    @staticmethod
    def from_fixed(fixed_srid):
        return GeoInfo(True, pd.DataFrame([]), [], fixed_srid)

    def is_geo_table(self, table_name):
        return self.is_geo_db and table_name in self.geo_tables

    def get_one_and_only_srid(self):
        unique_srids = self.srids.srid.unique()
        if len(unique_srids) > 1:
            raise RuntimeError(f"There were multiple srids {unique_srids} used in the database dump")
        if len(unique_srids) < 1:
            raise RuntimeError("There were no srids defined in the database dump")
        return unique_srids[0]

    def geo_info_for_table(self, table_name):
        if self.fixed_srid:
            return TableGeoInfo(self.fixed_srid, "geo", -1)

        row = self.srids[self.srids.table_name == table_name]
        if row.empty:
            return TableGeoInfo(self.get_one_and_only_srid(), "geo", -1)
        row = row.iloc[0]
        return TableGeoInfo(int(row.srid), row.geo_column, int(row.geometry_type))

    def get_most_frequent_srid(self):
        return TableGeoInfo(self.srids.srid.mode().iloc[0], "geo", -1)


class Schema:
    def __init__(self, df):
        self.df = df

    @staticmethod
    def from_file(filename):
        return Schema(pd.read_csv(filename))

    @staticmethod
    def from_str(string):
        return Schema(pd.read_csv(StringIO(string)))

    def get_create_sql(self, table_name):
        def row_to_str(r):
            s = f"{r['name']} {r['type']}"
            if r["notnull"]:
                s += " NOT NULL"
            if r["pk"]:
                s += " PRIMARY KEY"
            default = r["dflt_value"]
            if default is not None and not (isinstance(default, float) and np.isnan(default)):
                s += f" DEFAULT {default}"
            return s

        cols = [row_to_str(r) for r in self.df.to_dict(orient="records")]
        cols = ",\n".join([f"  {x}" for x in cols])
        return f"CREATE TABLE {table_name} (\n{cols}\n);"


def dumb_create_db_from_csvs(folder_name, db_name, clear_cache=False) -> None:
    """This method is useful for testing and creating a DB from a dir of csvs quickly without any assumptions about
    the structure of the database, just use pandas to read csvs and transcribe them directly into a new DB.
    """
    if exists(db_name):
        if not clear_cache:
            return
        os.unlink(db_name)

    with commit_and_close(db_name, missing_ok=True, spatial=True) as conn:
        dumb_load_database_from_csvs(folder_name, conn)


def dumb_load_database_from_csvs(folder_name, conn, if_exists="fail") -> None:
    csv_files = list(Path(folder_name).rglob("*.csv")) + list(Path(folder_name).rglob("*.zip"))
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        logger.info(f"Loading {df.shape[0]} records from {csv_file}")
        df.to_sql(csv_file.stem, con=conn, if_exists=if_exists, index=False)
        conn.commit()


def load_database_from_csvs(folder_name, conn, defaults_dir, signal=None) -> None:
    signal = signal or SIGNAL(object)

    geo_info = GeoInfo.from_folder(folder_name)

    conn.commit()
    curr = conn.cursor()
    # Erase default data for existing tables
    all_tables = [tn for tn in list_tables_in_db(curr) if not any(x.match(tn) for x in EXCL_NAME_PAT)]
    for table_name in all_tables:
        tn = "_".join(elem.capitalize() for elem in table_name.split("_"))
        curr.execute(f"Delete from {tn}")
    conn.commit()

    def find_data_files(dir):
        extensions = ["*.csv", "*.zip", "*.parquet", "*.h5", "*.hdf5"]
        files = [f for extension in extensions for f in glob.glob(f"{dir}/{extension}")]
        return [Path(x) for x in files if not x.lower().endswith("srids.csv")]

    data_files = find_data_files(folder_name)
    defined_table_names = [x.stem.lower() for x in data_files]

    # Add in default values (if they aren't in the dump)
    data_files += [x for x in find_data_files(defaults_dir) if x.stem.lower() not in defined_table_names]

    # Loading tables
    curr.execute("SELECT name FROM sqlite_master WHERE type ='table'")
    existing_tables = {x[0].lower(): x[0] for x in curr.fetchall()}

    if geo_info.is_geo_db:
        all_geo_types = dict(conn.execute("select f_table_name, geometry_type from geometry_columns"))
    else:
        all_geo_types = {}

    signal.emit(["start", "master", len(data_files), "Loading.."])

    for counter, data_file in enumerate(data_files):
        table_name = data_file.stem
        logger.debug(f"Restoring table {table_name}")
        signal.emit(["update", "master", counter + 1, "Loading.."])
        schema_name = data_file.with_suffix(".schema")

        # Load the schema
        if not os.path.isfile(schema_name):
            raise FileNotFoundError(f"Could not find schema dump for table {table_name}")

        # Schema based on the csvs - can be outdated because of needing migrations
        schema = pd.read_csv(schema_name)

        # Load the data
        print(data_file)
        df = df_from_file(data_file, low_memory=False)
        if df.empty:
            continue

        tn = existing_tables[table_name] if table_name in existing_tables else table_name
        # Existing schema based on a newly created database
        existing_schema = None
        if table_name.lower() in existing_tables:
            existing_schema = pd.read_sql_query(f"pragma table_info({table_name})", conn)

        df = _adjust_schemas(conn, tn, df, existing_schema, schema, geo_info)

        if geo_info.is_geo_table(table_name):
            insert_data_to_geo_table(all_geo_types, conn, df, geo_info, table_name, tn)
        else:
            columns = list(df.columns)
            columns = [x for x in columns if x != "geo_wkt" and not df[x].isna().all()]
            df[columns].to_sql(tn, con=conn, if_exists="append", index=False)


def insert_data_to_geo_table(all_geo_types, conn, df, geo_info, table_name, tn):
    table_geo = geo_info.geo_info_for_table(table_name)
    geo_col = f"{table_geo.geo_column}_wkt"
    non_geo_columns = [x for x in list(df.columns) if x != geo_col]
    col_quotes = [f'"{col}"' for col in non_geo_columns] + [table_geo.geo_column]
    columns = non_geo_columns + [geo_col]
    data = [[rec[col] for col in columns] + [table_geo.srid] for idx, rec in df.iterrows()]
    target_geo_type = table_geo.geo_type if table_name not in all_geo_types else all_geo_types[table_name]

    sql = f"""insert into "{tn}" ({",".join(col_quotes)}) VALUES({",".join(["?"] * (len(col_quotes) - 1))},"""
    if (target_geo_type > 3) and (table_geo.geo_type <= 3):
        sql += "CastToXY(CastToMulti(GeomFromText(?,?))))"
    else:
        sql += "CastToXY(GeomFromText(?,?)))"

    conn.executemany(sql, data)
    conn.commit()


def _handle_non_existing_table(conn, tname, df, schema, geo_info):
    all_geo_types = [x.upper() for x in list(spatialite_types.values())]
    columns = []
    geo_columns = []
    for _idx, rec in schema.iterrows():
        col_name = str(rec["name"])
        col_type = str(rec["type"])
        if col_type.upper() in all_geo_types:
            geo_columns.append([col_name, col_type])
            continue
        val = rec["dflt_value"]
        txt = f'"{col_name}" {col_type}'
        if int(rec["notnull"]):
            txt += " NOT NULL"
            if not val not in [np.nan, ""]:
                c_type = clean_sql_type(col_type, tname)
                dt = sql_to_numpy[c_type]
                if dt in [np.float_, np.int_]:
                    val = int(val) if not np.isnan(val) and int(val) == val else val
                txt += f" DEFAULT {val}"
        if int(rec["pk"]):
            txt += " PRIMARY KEY"
        columns.append(txt)

    # table does not exist in the standard and therefore we can create the table directly
    conn.execute(f'CREATE TABLE "{tname}" ({",".join(columns)})')
    for col_name, col_type in geo_columns:
        srid = geo_info.geo_info_for_table(tname).srid
        conn.execute(f"SELECT AddGeometryColumn( '{tname}', '{col_name}', {srid}, '{col_type}', 'XY');")
        conn.execute(f"SELECT CreateSpatialIndex( '{tname}' , '{col_name}' );")
    conn.commit()
    return df


def _adjust_schemas(
    conn, tname: str, df: DataFrame, existing_schema: Optional[DataFrame], schema: DataFrame, geo_info: GeoInfo
) -> DataFrame:
    if existing_schema is None:
        return _handle_non_existing_table(conn, tname, df, schema, geo_info)

    db_fields = sorted(existing_schema["name"])
    df_fields = sorted(schema["name"])

    lower_df_fields = [x.lower() for x in df_fields]
    lower_db_fields = [x.lower() for x in db_fields]

    # Collects all columns from both csv and db to not lose any data
    add_to_df = [x for x in db_fields if x.lower() not in lower_df_fields]
    add_to_db = [x for x in df_fields if x.lower() not in lower_db_fields]

    sz = df.shape[0]
    for new_fld in add_to_df:
        col_type = existing_schema[existing_schema["name"] == new_fld]["type"].values[0].upper()
        notnull = existing_schema[existing_schema["name"] == new_fld]["notnull"].values[0]
        dflt_value = existing_schema[existing_schema["name"] == new_fld]["dflt_value"].values[0]

        if not notnull:
            # We only need to add stuff to the DF if it is a mandatory column on SQLite
            continue

        col_type = clean_sql_type(col_type, tname)
        dt = sql_to_numpy[col_type]
        data = np.empty(sz, dtype=dt)  # type: np.ndarray
        if notnull and dflt_value:
            data.fill(dflt_value)
        df = df.assign(**{new_fld: data})

    for new_fld in add_to_db:
        col_type = schema[schema["name"] == new_fld]["type"].values[0]
        notnull = schema[schema["name"] == new_fld]["notnull"].values[0]
        dflt_value = schema[schema["name"] == new_fld]["dflt_value"].values[0]

        sql = f"""ALTER TABLE {tname} ADD column {new_fld} {col_type}"""

        if clean_sql_type(col_type, tname) == "TEXT":
            if isinstance(dflt_value, float) or isinstance(dflt_value, int):
                dflt_value = "''"

        if notnull:
            sql += " NOT NULL"
            if dflt_value is not None:
                sql += f" DEFAULT {dflt_value}"
        conn.execute(sql)
    conn.commit()

    return df
