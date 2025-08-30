# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from os.path import join

from polaris.utils.database.data_table_access import DataTableAccess


def export_zones_to_gmns(gmns_folder: str, target_crs, conn, path_to_file: PathLike):
    zones = DataTableAccess(path_to_file).get("Zone", conn=conn).to_crs(target_crs)

    zones["boundary"] = zones.geometry.to_wkt(rounding_precision=6)
    zones.drop(columns=["x", "y", "z", "area", "geo"], inplace=True)
    zones.rename(columns={"zone": "zone_id"}, inplace=True)
    zones.to_csv(join(gmns_folder, "zone.csv"), index=False)
