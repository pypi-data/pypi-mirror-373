# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from os.path import join, isfile

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from polaris.network.ie.gmns.importer.gmns_field_compatibility import zone_field_translation
from polaris.network.ie.gmns.importer.util_functions import add_required_fields
from polaris.network.utils.srid import get_srid


def import_gmns_zones(gmns_folder: str, source_crs, proj_crs, conn):
    logging.info("Importing Zones")
    zone_file = join(gmns_folder, "zone.csv")

    if not isfile(zone_file):
        return

    # We import zones
    zones = pd.read_csv(zone_file)

    # Fields that are completely empty don't need to be imported
    zones.dropna(how="all", axis=1, inplace=True)

    if "boundary" not in zones:
        return

    # We rename the fields to be compatible with Polaris
    zones.rename(columns=zone_field_translation, inplace=True, errors="ignore")

    geos = gpd.GeoSeries.from_wkt(zones.geo).set_crs(source_crs).to_crs(proj_crs)
    zones.geo = np.array([shapely.to_wkt(geo, rounding_precision=6) for geo in geos])

    add_required_fields(zones, "zone", conn)
    # We check if we are importing from an OSM network and if we should keep the IDs
    data_cols = [str(c) for c in zones.columns if c != "geo"]
    cols = ",".join(data_cols) + ",geo"
    param_bindings = ",".join(["?"] * len(data_cols)) + ",GeomFromText(?, ?)"
    sql = f"INSERT INTO zone({cols}) VALUES({param_bindings})"

    zones = zones.assign(srid=get_srid(conn=conn))
    data_cols.extend(["geo", "srid"])
    zones = zones[data_cols]

    conn.executemany(sql, zones[data_cols].to_records(index=False))
    conn.commit()
