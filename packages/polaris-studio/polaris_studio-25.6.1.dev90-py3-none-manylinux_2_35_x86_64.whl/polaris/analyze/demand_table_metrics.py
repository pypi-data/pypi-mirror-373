# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from pathlib import Path

import numpy as np
import pandas as pd

from polaris.skims.memory_matrix import MemoryMatrix
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.db_utils import read_and_close, has_table


class DemandTableMetrics:
    def __init__(self, supply_file: PathLike, demand_file: PathLike):
        """
        :param supply_file: Path to the supply file corresponding to the demand file we will compute metrics for
        :param demand_file: Path to the demand file we want to compute metrics for
        """
        self.__demand_file__ = ScenarioCompression.maybe_extract(Path(demand_file))
        self.__supply_file__ = supply_file
        self.__zones = pd.DataFrame([])
        self.__loc_zn = pd.DataFrame([])
        self.__agg_type = ""
        self.load_all_data = True
        with read_and_close(self.__demand_file__) as conn:
            if has_table(conn, "Mode"):
                modes = DataTableAccess(self.__demand_file__).get("Mode", conn).query("mode_id<1000")
                self.__modes__ = dict(zip(modes["mode_id"], modes["mode_description"]))
            else:

                self.__modes__ = {
                    0: "SOV",
                    4: "BUS",
                    5: "RAIL",
                    7: "BYCICLE",
                    8: "WALK",
                    9: "TAXI",
                    10: "SCHOOLBUS",
                    17: "MD_TRUCK",
                    18: "HD_TRUCK",
                    19: "BPLATE",
                    20: "LD_TRUCK",
                }

    def _build_aggregate_matrices(self, df: pd.DataFrame, matrix_names: list, column="zone") -> MemoryMatrix:
        from scipy.sparse import coo_matrix

        if self.__loc_zn.empty or self.__agg_type != column:
            # The location/zone relationship
            self.__agg_type = column
            self.__loc_zn = DataTableAccess(self.__supply_file__).get("location").reset_index()[["location", column]]
            self.__loc_zn.rename(columns={column: "agg_field"}, inplace=True)

            # List of zones or counties
            if column == "zone":
                zn = np.sort(DataTableAccess(self.__supply_file__).get("zone").zone.to_numpy())
            else:
                zn = np.sort(DataTableAccess(self.__supply_file__).get("counties").county.to_numpy())

            self.__zones = pd.DataFrame({"agg_field": zn, "seq_id": np.arange(zn.shape[0])})
            self.__loc_zn = self.__loc_zn.merge(self.__zones, on="agg_field", how="left").drop(columns=["agg_field"])

        if "mode_desc" not in df.columns:
            df_aux = pd.DataFrame({"mode_id": self.__modes__.keys(), "mode_desc": self.__modes__.values()})
            df = df.merge(df_aux, on="mode_id", how="left")

        dt = df.merge(self.__loc_zn, left_on="origin", right_on="location", how="left")
        dt = dt.drop(columns=["location"]).rename(columns={"seq_id": "origin_zone"})

        dt = dt.merge(self.__loc_zn, left_on="destination", right_on="location", how="left")
        dt = dt.drop(columns=["location"]).rename(columns={"seq_id": "destination_zone"})
        dt = dt[["origin_zone", "destination_zone", "mode_desc"]]

        with read_and_close(self.__demand_file__) as conn:
            fac = conn.execute("SELECT infovalue from About_Model where infoname=='abs_pop_sample_rate'").fetchone()
            factor = float(fac[0]) if fac else 1.0

        num_zones = self.__zones.shape[0]
        matrices = {}
        for mode_name in matrix_names:
            df = dt[dt.mode_desc == mode_name]
            if df.empty:
                continue
            df = df.groupby(["origin_zone", "destination_zone"]).size().reset_index(name="trips")
            orig_zones = df.origin_zone.to_numpy()
            dest_zones = df.destination_zone.to_numpy()
            m = coo_matrix((df.trips.to_numpy(), (orig_zones, dest_zones)), shape=(num_zones, num_zones)).toarray()
            matrices[mode_name] = m / factor

        matrix = MemoryMatrix(data=matrices)
        matrix.index = self.__zones.agg_field.to_numpy()

        return matrix
