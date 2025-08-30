# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import math

import pandas as pd


def log_data(data, columns, index=None):
    index = index or columns[0:2]
    logging.info("\n\t" + pd.DataFrame(data, columns=columns).set_index(index).to_string().replace("\n", "\n\t") + "\n")


def calculate_mse(simulated, target):
    if target is None:
        return -2
    sample_size, total_error_sq = 0, 0.0
    # for key in set.intersection(set(target.keys()), set(simulated.keys())):
    for key, t_value in target.items():
        s_value = simulated.get(key, 0)
        if s_value > 0 and t_value > 0:
            sample_size += 1
            total_error_sq += math.pow(t_value - s_value, 2)
    return total_error_sq / sample_size if sample_size > 0 else -1


def calculate_rmse(simulated, target):
    if target is None:
        return -2
    mse = calculate_mse(simulated, target)
    return math.sqrt(mse) if mse != -1 else -1


def calculate_normalized_rmse(simulated, target):
    if target is None:
        return -2
    rmse = calculate_rmse(simulated, target)
    sample_size, total_target = 0, 0.0
    for key in set.intersection(set(target.keys()), set(simulated.keys())):
        if simulated[key] > 0 and target[key] > 0:
            sample_size += 1
            total_target += target[key]
    return rmse / (total_target / sample_size) if rmse != -1 else -1
