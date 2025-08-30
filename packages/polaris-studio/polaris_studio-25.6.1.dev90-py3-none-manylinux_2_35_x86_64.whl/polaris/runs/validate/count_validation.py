# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import pandas as pd

from polaris.runs.results.h5_results import H5_Results
from polaris.runs.results.link_volumes import melt_AB_direction


def load_targets(csv_file):
    if not csv_file.exists():
        return None, None
    period_file = str(csv_file).replace(".csv", ".periods.csv")
    periods = list(pd.read_csv(period_file).values)
    target = pd.read_csv(csv_file)
    target = melt_AB_direction(target, column_variable="period", value_name="observed_volume")
    target = _add_daily(target, "observed_volume")
    target = target.set_index(["link", "direction", "period"])

    return target, periods


def load_simulated(h5_file, population_scale_factor, periods):
    results = H5_Results(h5_file)
    simulated = results.get_link_volumes(population_scale_factor, periods).reset_index()
    simulated = melt_AB_direction(simulated, column_variable="period", value_name="simulated_volume")
    simulated = _add_daily(simulated, "simulated_volume")
    simulated = simulated.set_index(["link", "direction", "period"])
    return simulated


def _add_daily(df, col_name):
    if "daily" in [e.lower() for e in df.period.unique()]:
        return df

    agg = {e: "first" for e in df.columns if e not in ["link", "direction", col_name]}
    agg[col_name] = lambda x: x.sum(min_count=1)  # Using the min_count argument to prevent summing NaN to 0
    daily_vals = df.groupby(["link", "direction"]).agg(agg).reset_index().assign(period="Daily")
    return pd.concat([df, daily_vals])
