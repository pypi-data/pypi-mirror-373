# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from os import PathLike
from os.path import join, isfile

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import shapely.wkt

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.ie.gmns.importer.add_land_uses import add_land_uses
from polaris.network.ie.gmns.importer.gmns_field_compatibility import location_field_translation
from polaris.network.ie.gmns.importer.util_functions import add_required_fields
from polaris.network.starts_logging import logger
from polaris.network.tools.geo import Geo
from polaris.network.utils.srid import get_srid


def import_gmns_locations(gmns_folder: str, source_crs, proj_crs, conn, path_to_file: PathLike):
    logging.info("Importing Locations")

    # Thorough documentation of the assumptions used in this code is provided
    # with the package documentation -> Supply/Import-Export/GMNS
    location_file = join(gmns_folder, "location.csv")
    if not isfile(location_file):
        logger.info("No location file to import from GMNS")
        return

    locs = pd.read_csv(location_file)

    locs.rename(columns=location_field_translation, inplace=True, errors="ignore")
    locs.dropna(how="all", axis=1, inplace=True)

    if "x" not in locs or "y" not in locs:
        logger.error("Location file does not have coordinates.  Import through lr/offset not supported")
        return

    if "x" not in locs or "y" not in locs:
        logger.error("Location file does not have coordinates.  Import through lr/offset not supported")
        return

    for table in ["Zone", "Link"]:
        if DataTableAccess(path_to_file).get(table, conn=conn).empty:
            logger.error(f"We cannot import locations without importing {table} first, and that table is empty")
            return

    geos = gpd.points_from_xy(locs.x, locs.y, crs=source_crs).to_crs(proj_crs)
    locs = locs.assign(geo=np.array([shapely.to_wkt(geo, rounding_precision=6) for geo in geos]))

    add_land_uses(locs, conn, path_to_file)

    add_required_fields(locs, "location", conn)

    geotool = Geo(path_to_file)
    for idx, rec in locs.iterrows():  # type: ignore
        loc_geo = shapely.wkt.loads(rec.geo)
        locs.at[idx, "zone"] = geotool.get_geo_item("zone", loc_geo)
        lnk = geotool.get_geo_item("link", loc_geo)
        if lnk >= 0:
            locs.loc[[idx], "link"] = lnk

    cols = [str(x) for x in locs.columns]
    cols.remove("geo")
    cols.append("geo")

    param_bindings = f'{",".join(["?"] * (len(cols) - 1))}, GeomFromText(?,{get_srid(conn=conn)})'
    sql = f'INSERT INTO Location ({",".join(cols)}) VALUES({param_bindings})'

    conn.executemany(sql, locs[cols].to_records(index=False))
    conn.commit()
