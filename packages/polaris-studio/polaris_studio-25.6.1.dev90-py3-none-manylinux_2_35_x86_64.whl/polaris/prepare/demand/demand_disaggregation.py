# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

import logging
from itertools import chain

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from polaris.utils.database.db_utils import read_and_close
from polaris.utils.pandas_utils import stochastic_round
from polaris.utils.python_signal import PythonSignal


def disaggregate_column(df, col_name, locations):
    df = pd.DataFrame(df[["zone_origin", "zone_dest", col_name]])

    # Convert each row with "N" trips into N rows with 1 trip
    df[col_name] = stochastic_round(df[col_name])  # integerize the column first
    df = df.loc[df.index.repeat(df[col_name])]
    df = df.reset_index(drop=True).reset_index().rename(columns={"index": "trip_id"})

    df["origin_location"] = np.nan
    df["dest_location"] = np.nan
    no_location_zones = set()

    def convert_zone_to_location(zone_col, loc_col, zone_id):
        n_trips = df.loc[df[zone_col] == zone_id].shape[0]
        locations_ = locations.loc[locations.zone == zone_id]
        if locations_.shape[0] == 0:
            no_location_zones.add(zone_id)
            return
        sampled_locations = locations_.sample(n=n_trips, replace=True).reset_index(drop=True)
        df.loc[df[zone_col] == zone_id, loc_col] = sampled_locations["location"].values

    zones = set.union(set(df.zone_origin.unique()), set(df.zone_dest.unique()))
    pbar = PythonSignal(object)
    pbar.emit(["start", "master", len(zones), "Randomly assigning destination locations"])
    for i_, zone_id in enumerate(zones):
        convert_zone_to_location("zone_origin", "origin_location", zone_id)
        convert_zone_to_location("zone_dest", "dest_location", zone_id)
        pbar.emit(["update", "master", i_, "Randomly assigning destination locations"])

    na_trips = df.loc[df.origin_location.isna() | df.dest_location.isna()].shape[0]
    if na_trips:
        logging.info(f"There were {na_trips} trips to/from a zone with no appropriate locations")
        logging.info(f"The zone(s) [{str(no_location_zones).strip('{}')}] have no appropriate locations.")

    df = df.drop(columns=["zone_origin", "zone_dest", col_name])
    return df.loc[~df.origin_location.isna() & ~df.dest_location.isna()]


def load_crosswalk(csv_file):
    df = pd.read_csv(csv_file)
    assert "TAZ" in df.columns
    assert "zone" in df.columns
    return df


def load_locations(supply_db, disallowed_lu_types=None):

    disallowed_lu_types = (
        disallowed_lu_types if disallowed_lu_types is not None else ["RESIDENTIAL-SINGLE", "RESIDENTIAL-MULTI"]
    )

    sql = "SELECT location, zone, land_use FROM Location"
    if disallowed_lu_types:
        types = ",".join([f"'{t}'" for t in disallowed_lu_types])
        sql += f" WHERE land_use NOT IN ({types})"

    with read_and_close(supply_db) as conn:
        df = pd.read_sql_query(sql, conn)
        assert df.shape[0] > 0
        return df


def plot_temporal_dist(df, label):
    df = df.copy()
    df["hour"] = round(df.minute / 60.0, 1)
    plt.gca().plot(df.hour, 60.0 * df.proportion, label=label)


def assign_random_start_time(trips, temporal_dist):

    minutes_in_day = list(range(0, 24 * 60))
    assert len(minutes_in_day) == temporal_dist.shape[0], f"{len(minutes_in_day)} != {temporal_dist.shape[0]}"
    trips["start_min"] = np.random.choice(minutes_in_day, size=trips.shape[0], p=temporal_dist.proportion)
    trips["start_sec"] = 60 * trips.start_min + np.random.choice(list(range(0, 60)), size=trips.shape[0])
    return trips


def subset_temporal_dist(df, hour_ranges):
    minutes_to_keep = list(chain.from_iterable(list(range(int(r[0] * 60), int(r[1] * 60))) for r in hour_ranges))
    df = df.copy()
    df.loc[~df.minute.isin(minutes_to_keep), "proportion"] = 0
    df["proportion"] = df["proportion"] / df["proportion"].sum()
    return df


def translate_period_proportion_to_hourly(df):
    """
    Converts a dataframe with proportions specified by start/end hour into a dataframe
    with a proportion for each individual hour.
    """

    assert sorted(df.columns) == [
        "end_hour",
        "proportion",
        "start_hour",
    ], f"input df has incorrect headers, {df.columns}"

    df["minute"] = df.apply(lambda r: list(range(int(r["start_hour"] * 60), int(r["end_hour"] * 60))), axis=1)
    df["proportion"] = df.proportion.astype(float) / (df.end_hour - df.start_hour).astype(float)
    df = df.explode("minute")[["proportion", "minute"]]  # .rename(columns={"mintu": "hour"})
    # assert list(range(0, 24)) == list(df.hour.unique())

    df["proportion"] = df["proportion"] / df["proportion"].sum()
    return df
