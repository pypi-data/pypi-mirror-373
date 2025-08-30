# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import Iterable, Optional
import numpy as np


def _distribute_input_check(x: float, splits: Iterable[float], weights: Optional[Iterable[float]] = None):
    splits = np.array(splits)
    if np.all(splits == 0):
        raise ValueError("splits cannot be all zeros.")
    if x < 0:
        raise ValueError("x cannot be negative.")
    if weights is None:
        weights = np.ones(len(splits))
    else:
        weights = np.array(weights)
    if np.all(weights == 0):
        raise ValueError("weights cannot be all zeros.")
    if len(splits) != len(weights):
        raise ValueError("splits and weights must have the same length.")
    return splits, weights


def distribute_avg(avg: float, splits: Iterable[float], weights: Optional[Iterable[float]] = None) -> Iterable[float]:
    splits, weights = _distribute_input_check(avg, splits, weights)
    return splits * avg * weights.sum() / (splits * weights).sum()


def distribute_sum(sum_: float, splits: Iterable[float], weights: Optional[Iterable[float]] = None) -> Iterable[float]:
    splits, weights = _distribute_input_check(sum_, splits, weights)
    return splits * sum_ / (splits * weights).sum()


def military_time_to_minutes(ti):
    return (ti // 100) * 60 + (ti % 100)
