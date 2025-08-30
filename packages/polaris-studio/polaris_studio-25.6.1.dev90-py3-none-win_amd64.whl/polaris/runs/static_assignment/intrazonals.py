# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import numpy as np


# We need to fill the diagonal with something, so we get the smallest
def fill_intrazonals(arr: np.ndarray):
    second_smallest = np.apply_along_axis(lambda x: np.sort(x)[1], axis=1, arr=arr)
    np.fill_diagonal(arr, second_smallest)
    return arr
