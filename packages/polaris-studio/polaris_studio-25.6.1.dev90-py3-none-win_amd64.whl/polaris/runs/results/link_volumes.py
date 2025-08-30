# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

import warnings
import pandas as pd
import numpy as np

from typing import Optional, List, Tuple
from scipy.stats import linregress  # type: ignore

MINUTES_IN_DAY = 24 * 60


def pivot_to_AB_direction(df: pd.DataFrame):
    """Converts a dataframe with link UUID as the index to have col_ab, col_ba format."""
    dirs = (df.index % 2).map({0: "AB", 1: "BA"})
    ab_df = df.loc[dirs == "AB"]
    ab_df.columns = [f"{c}_AB" for c in ab_df.columns]
    ab_df.index = ab_df.index // 2
    ab_df.index.name = "link"
    ba_df = df.loc[dirs == "BA"]
    ba_df.columns = [f"{c}_BA" for c in ba_df.columns]
    ba_df.index = ba_df.index // 2
    ba_df.index.name = "link"
    return ab_df.join(ba_df)


def melt_AB_direction(df, column_variable="value_type", value_name="value"):
    """
    Converts a dataframe with col_ab, col_ba format into a tall format where 'col' is stored in
    the column_variable column, AB is stored in the direction column and the corresponding value
    from col_ab is stored in the "value_name" column.
    """
    undir_cols = [c for c in df.columns if not (c.endswith("_AB") or c.endswith("_BA"))]
    df = df.melt(id_vars=undir_cols, var_name="XXX", value_name=value_name)
    df[column_variable] = df["XXX"].str.split("_").str[0]
    df["direction"] = df["XXX"].str.split("_").str[-1]
    return df.drop(columns=["XXX"])


def aggregate_link_volumes(link_vols: pd.DataFrame, periods: Optional[List[Tuple[str, int, int]]], agg_func="sum"):
    if periods is None:
        periods = [("Daily", 0, 1440)]
    assert len(link_vols) == MINUTES_IN_DAY

    period_vec, period_names = _construct_period_mapping(periods)
    agg_df = pd.DataFrame(index=link_vols.columns)
    for period_id in set(period_vec):
        agg_df[period_names[period_id]] = link_vols.loc[period_vec == period_id].agg(agg_func, axis=0)
    return agg_df


def _construct_period_mapping(periods):
    period_vec = np.full(MINUTES_IN_DAY, -1)
    period_names = {i: n for i, n in enumerate({n for n, _, _ in periods})}
    period_ids = {n: i for i, n in period_names.items()}
    for period_name, start, end in periods:
        period_vec[int(start) : int(end)] = period_ids[period_name]

    if -1 in period_vec:
        not_assigned_ids = [i for i, x in enumerate(period_vec) if x == "_NOT_ASSIGNED"]
        raise ValueError(f"Some minutes are not assigned to any period. Example: {not_assigned_ids[:5]}")
    return period_vec, period_names


def get_ols_stats(x, y):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reg = linregress(x, y)
            return reg, rf"$y \approx {reg.slope:.2f}x {reg.intercept:+.1f}$" + "\n" + f"$R^2={pow(reg.rvalue, 2):.3f}$"
    except Exception:
        return None, "Bad-fit for OLS"
