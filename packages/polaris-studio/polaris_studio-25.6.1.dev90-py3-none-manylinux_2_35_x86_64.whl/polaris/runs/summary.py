# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from glob import glob
from os.path import join
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


def load_summary(summary_path, raise_on_error=True, drop_last_minute=True):
    try:
        df = pd.read_csv(summary_path, index_col=False, on_bad_lines="warn")
        if drop_last_minute:
            df = df[df.simulated_time < (86400 - 60)]
        if df["pax_in_network"].isna().any():
            logging.warning(f"Error while reading file ({summary_path}), last 10 lines are: ")
            with open(summary_path, "r") as f:
                for line in f.readlines()[-10:]:
                    logging.info(line.strip())
            if raise_on_error:
                raise ValueError("BLAH")
            else:
                # We are using pax_in_network column to look for mis-formed csv files
                # if we are ignoring errors - just drop any rows where this column is NA
                return df[~df["pax_in_network"].isna()]
        return df
    except EmptyDataError:
        # After certain conditions (i.e. warm start) no summary file will be generated
        return None


def parse_row(row):
    print(f"row = {row}")
    for col, parser in summary_types.items():
        row[col] = parser(row[col])
    return row


def time_parser(val):
    h, m, s = map(int, val.split(":"))
    return h * 3600 + 60 * m + s


summary_types = {"time": time_parser, "departed": int}


def find_summary_files(base_dir):
    return sorted(glob(join(base_dir, f"*", "summary*.csv")), key=os.path.getmtime)


def aggregate_summaries(base_dir, save=True):
    summary_list = find_summary_files(base_dir)

    if len(summary_list) == 0:
        logging.info(f"No summary files found in directory: {base_dir}")
        return pd.DataFrame()

    df = aggregate_summaries_from_list(summary_list)
    if save:
        df.to_csv(base_dir / "aggregate_summary.csv", index=False)

    return df


def aggregate_summaries_from_list(summary_list):
    dfs = []
    for i, summary in enumerate(summary_list):
        name = Path(summary).parent.name
        try:
            s = pd.read_csv(summary, index_col=False)
            s = s[["time", "in_network", "pax_in_network"]]
        except pd.errors.EmptyDataError:
            continue

        # For the first valid summary file - use the date index column, for all others drop it
        if dfs:
            s = s.drop(columns="time")

        s = s.rename(columns={"in_network": f"{name}_in_network", "pax_in_network": f"{name}_pax_in_network"})
        dfs.append(s)

    return pd.concat(dfs, axis=1)
