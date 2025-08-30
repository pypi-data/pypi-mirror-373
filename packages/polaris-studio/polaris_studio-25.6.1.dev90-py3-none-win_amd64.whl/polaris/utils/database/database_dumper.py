# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd

from polaris.network.utils.srid import get_table_srid
from polaris.utils.database.db_utils import list_tables_in_db
from polaris.utils.database.spatialite_utils import is_spatialite
from polaris.utils.dir_utils import mkdir_p
from polaris.utils.file_utils import df_to_file
from polaris.utils.signals import SIGNAL
from polaris.utils.structure_finder import find_table_fields

EXCL_NAME_PAT = [
    re.compile(e)
    for e in (
        "data_licenses",
        "geometry_columns",
        "spatial_ref_sys",
        "spatialite_history",
        "knn",
        "sql_statements_log",
        "sqlite_sequence",
        "views_geometry",
        "virts_geometry",
        "spatialindex",
        "elementarygeometries",
        "sqlite_stat",
        "table_metadata",
        "sequence",
        "metadata",
        "raster_coverages",
        "rl2map_configurations",
        "topologies",
        "^iso_metadata",
        "vector_coverages",
        "networks",
        "^idx_",
        "^se_",
        "^stored_",
        "^wms_",
    )
]


def dump_database_to_csv(
    conn,
    folder_name,
    signal=None,
    exclude_patterns=None,
    include_patterns=None,
    ext="csv",
    table_list=None,
    target_crs=None,
) -> None:
    signal = signal or SIGNAL(object)
    exclude_patterns = exclude_patterns or EXCL_NAME_PAT

    folder_name = Path(folder_name)
    mkdir_p(folder_name)

    if is_spatialite(conn):
        geo_cols = get_table_data(conn, "geometry_columns")[
            ["f_table_name", "f_geometry_column", "geometry_type", "srid"]
        ]
        geo_cols.columns = ["table_name", "geo_column", "geometry_type", "srid"]
        geo_cols = geo_cols[geo_cols.table_name != "iso_metadata"]  # remove iso_metatable (standard Spatialite)
        if target_crs is not None:
            geo_cols.srid = target_crs
        geo_cols.to_csv(folder_name / "srids.csv", index=False)

    if table_list is not None:
        assert include_patterns is None

    all_tables = [tn for tn in list_tables_in_db(conn) if not any(x.match(tn) for x in exclude_patterns)]
    if include_patterns is not None:
        include_patterns = [re.compile(p) if isinstance(p, str) else p for p in include_patterns]
        all_tables = [tn for tn in all_tables if any(x.match(tn) for x in include_patterns)]

    if table_list is not None:
        table_list = [tn.lower() for tn in table_list]
        all_tables = [tn for tn in all_tables if tn.lower() in table_list]

    txt = "Dumping database"
    signal.emit(["start", "master", len(all_tables), txt])

    for i, table_name in enumerate(all_tables):
        # get the schema and the table
        schema = pd.read_sql_query(f"pragma table_info({table_name})", conn)
        data = get_table_data(conn, table_name, target_crs).round(decimals=6)

        # Enforces integer format if type is integer
        for col in schema[schema["type"] == "INTEGER"]["name"].str.lower().tolist():
            if pd.isna(data[col]).any():
                continue
            data[col] = data[col].astype(np.int64)

        # check if the table exists in another format
        use_ext = ext
        if not (folder_name / f"{table_name}.{use_ext}").exists():
            for f_ext in ["csv", "parquet", ".hdf5", ".h5", ".zip"]:
                if (folder_name / f"{table_name}.{f_ext}").exists():
                    use_ext = f_ext
            if use_ext != ext:
                logging.warning(f"Table {table_name} exists in {use_ext}. Using that format for this table instead.")

        # Let's not dump empty tables
        if data.empty:
            (folder_name / f"{table_name}.{use_ext}").unlink(missing_ok=True)
            (folder_name / f"{table_name}.schema").unlink(missing_ok=True)
        else:
            df_to_file(data, folder_name / f"{table_name}.{use_ext}", index=False)
            schema.to_csv(folder_name / f"{table_name}.schema", index=False)

        signal.emit(["update", "master", i, table_name, txt])

    signal.emit(["finished_dumping_procedure"])


def get_table_data(conn, table_name, target_crs=None):
    import geopandas as gpd

    fields, _, geo_field = find_table_fields(conn, table_name)
    fields = [f'"{x}"' for x in fields if '"' not in x]
    if geo_field is None:
        keys = ",".join(fields)
        df = pd.read_sql_query(f"select {keys} from '{table_name}'", conn)
    else:
        fields.append(f"Hex(ST_AsBinary({geo_field})) as geo")
        keys = ",".join(fields)
        sql = f"select {keys} from '{table_name}';"
        df = pd.read_sql(sql, conn)
        df.loc[df.geo.isin(["", b""]), "geo"] = None
        geo_data = gpd.GeoSeries.from_wkb(df.geo, crs=get_table_srid(conn, table_name))
        if target_crs is not None:
            geo_data = geo_data.to_crs(target_crs)
        # The replaces are needed to match differences in the WKT format we get with this change
        df[f"{geo_field}_wkt"] = geo_data.to_wkt(rounding_precision=8).str.replace(" (", "(").str.replace(", ", ",")
        df = df.drop(columns=["geo"])

    df.columns = [x.lower() for x in df.columns]
    return df
