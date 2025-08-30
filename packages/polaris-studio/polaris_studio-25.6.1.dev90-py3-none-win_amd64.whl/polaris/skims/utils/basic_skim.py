# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import importlib.util as iutil
from os import PathLike
from pathlib import Path

import numpy as np
import pandas as pd

INFINITE_TRANSIT = 1e6

if iutil.find_spec("geopandas") is not None:
    from geopandas import GeoDataFrame as gdf
else:
    from pandas import DataFrame as gdf


class SkimBase:
    def __init__(self):
        self.version = "omx"
        self._inf = np.inf
        self.zone_id_to_index_map = {}
        self.zone_index_to_id_map = {}
        self.index = pd.DataFrame([])
        self.intervals = []

    @classmethod
    def from_file(self, path_to_file: PathLike):
        mat = self()
        mat.open(path_to_file)
        return mat

    @property
    def num_zones(self) -> int:
        return self.index.shape[0]

    def open(self, path_to_file: PathLike):
        """Method overloaded by each skim class type"""
        pass

    def __setattr__(self, key, value):
        self.__dict__[key] = value

        if key != "index":
            return
        self.zone_id_to_index_map.clear()
        self.zone_index_to_id_map.clear()

        if not value.empty:
            self.zone_id_to_index_map = dict(zip(value.zones, value.index))
            self.zone_index_to_id_map = dict(zip(value.index, value.zones))

    def convert_zoning_systems(self, source_zoning: gdf, target_zoning: gdf, output_path: Path):
        """Converts the zoning system of the skims

        Args:
            *src_zone* (:obj:`gpd.GeoDataFrame`): GeoDataFrame with the source zoning system
            *tgt_zone* (:obj:`gpd.GeoDataFrame`): GeoDataFrame with the target zoning system
            *output_path* (:obj:`Path`): Path to the output file
        """
        from polaris.skims.utils.zoning_conversion import convert_zoning_systems

        convert_zoning_systems(self, source_zoning, target_zoning, output_path)
