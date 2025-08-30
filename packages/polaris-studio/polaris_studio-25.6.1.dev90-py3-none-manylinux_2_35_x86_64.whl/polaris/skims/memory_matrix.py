# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import Dict, Optional

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from numpy.typing import NDArray


class MemoryMatrix:
    """
    A class to represent a memory matrix for storing and retrieving data.
    """

    def __init__(self, data: Optional[Dict[str, NDArray]] = None):
        """
        Initializes the memory matrix with a given size.

        :param size: The size of the memory matrix.
        """
        self.__data = data or {}
        self.index = np.array([], np.int64)

    def get_matrix(self, core: str) -> NDArray:
        """Returns the data for a matrix core

        :Arguments:
            **core** (:obj:`str`): name of the matrix core to be returned

            **copy** (:obj:`bool`, *Optional*): return a copy of the data. Defaults to False

        :Returns:
            **object** (:obj:`np.ndarray`): NumPy array
        """
        if core not in self.matrices:
            raise AttributeError("Matrix core does not exist in this matrix")
        return self.__data[core]

    def to_aeq(self):
        # deferred import of Aeq as it is not a core dependency
        from aequilibrae.matrix import AequilibraeMatrix

        if self.zones <= 0 or not self.matrices:
            raise ValueError("Cannot convert to AequilibraeMatrix: no data available")

        mat = AequilibraeMatrix()
        mat.create_empty(memory_only=True, zones=self.zones, matrix_names=self.matrices)
        mat.index[:] = self.index[:]
        for i, core in enumerate(self.matrices):
            mat.matrices[:, :, i] = self.__data[core][:, :]
        return mat

    def to_df(self):
        """Converts the memory matrix to a DataFrame format.

        :Returns:
            **object** (:obj:`pd.DataFrame`): DataFrame with matrix data
        """
        if not self.matrices:
            raise ValueError("Cannot convert to DataFrame: no data available")

        matrices_df = pd.DataFrame([])
        mat_ids = self.index
        for x, mat in self.__data.items():
            coo_ = coo_matrix(mat)
            df = pd.DataFrame({"from_id": mat_ids[coo_.row], "to_id": mat_ids[coo_.col], x: coo_.data})
            ab_flows = df.query("from_id < to_id").set_index(["from_id", "to_id"])
            ba_flows = df.query("from_id > to_id").rename(columns={"from_id": "to_id", "to_id": "from_id"})
            ba_flows.set_index(["from_id", "to_id"], inplace=True)
            flows = ab_flows.join(ba_flows, how="outer", lsuffix="_ab", rsuffix="_ba").fillna(0)
            flows[f"{x}_tot"] = flows[f"{x}_ab"] + flows[f"{x}_ba"]

            matrices_df = flows if matrices_df.empty else matrices_df.join(flows, how="outer")
        matrices_df = matrices_df.fillna(0).reset_index()
        return matrices_df

    @property
    def matrices(self):
        """Returns the list of matrix names in this memory matrix"""
        return sorted(self.__data.keys())

    @property
    def zones(self):
        """Returns the number of zones in this matrix"""
        return self.index.shape[0]

    def __getattr__(self, mat_name: str):
        if mat_name in object.__dict__:
            return self.__dict__[mat_name]

        if mat_name in self.matrices:
            return self.get_matrix(mat_name)
