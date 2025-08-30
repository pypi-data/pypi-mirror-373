# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from statistics import mean
from typing import List

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


def compare_tables(old_df: pd.DataFrame, new_df: pd.DataFrame) -> List[str]:
    report = []
    # identifies missing fields
    added_fields = [x for x in new_df.columns if x not in old_df.columns]
    if added_fields:
        report.append(f"    * Fields added to table: {', '.join(added_fields)}")
    removed_fields = [x for x in old_df.columns if x not in new_df.columns]
    if removed_fields:
        report.append(f"    * Fields removed from table: {', '.join(removed_fields)}")

    # Make sure that we have the overlapping fields in the same order
    kept_fields = [x for x in new_df.columns if x in old_df.columns]
    new_df = new_df[kept_fields]
    old_df = old_df[kept_fields]

    # identifies missing records
    newrec = new_df[~new_df.index.isin(old_df.index)]
    if not newrec.empty:
        report.append(f"     * {newrec.shape[0]:,} records added to table")

    drc = old_df[~old_df.index.isin(new_df.index)]
    if not drc.empty:
        report.append(f"     * {drc.shape[0]:,} records deleted from table")

    new_df = new_df.loc[new_df.index.isin(old_df.index), :].sort_index()
    old_df = old_df.loc[old_df.index.isin(new_df.index), :].sort_index()

    if old_df.index.has_duplicates or new_df.index.has_duplicates:
        report.extend(compare_with_duplicates(old_df, new_df))
    else:
        report.extend(compare_straight_tables(old_df, new_df))
    return report


def compare_straight_tables(old_df: pd.DataFrame, new_df: pd.DataFrame) -> List[str]:
    report = []

    # Execute comparison
    compare = new_df.compare(old_df, align_axis=1, result_names=("new_table", "old_table"))

    if compare.empty:
        return []

    report.append(f"    * There are differences in {compare.shape[0]:,} records in total")
    # Lists the columns with differences
    diff_fields = list({x[0] for x in compare.columns})
    report.append(f"    * There are differences in {len(diff_fields)} fields")

    for field in diff_fields:
        field_df = pd.DataFrame(compare[[field]])
        field_df.columns = [x[1] for x in field_df.columns]  # type: ignore
        field_df.dropna(inplace=True)
        if field_df.empty:
            continue
        report.append(f"""      * Field "{field}":""")
        report.append(f"          * There are differences in {field_df.shape[0]:,} records")

        # If numeric, we compare values
        if is_numeric_dtype(field_df["new_table"]) and is_numeric_dtype(field_df["old_table"]):
            field_df = field_df.assign(diff_value=field_df.new_table - field_df.old_table)
            report.extend(
                [
                    f"        * Maximum (new - old) difference: {round(np.nanmax(field_df.diff_value), 5)}",
                    f"        * Maximum negative (new - old) difference: {round(np.nanmin(field_df.diff_value))}",
                    f"        * Median absolute difference: {round(np.nanmedian(field_df.diff_value.abs()), 5)}",
                    f"        * Mean absolute difference: {round(np.nanmean(field_df.diff_value.abs()), 5)}",
                ]
            )

    return report


def compare_with_duplicates(old_df: pd.DataFrame, new_df: pd.DataFrame) -> List[str]:
    changes = []
    diff_in_records = []
    unique_indices = old_df.index.unique()
    for idx_val in unique_indices:
        df1 = old_df.loc[idx_val, :]
        df2 = new_df.loc[idx_val, :]
        if df1.shape[0] != df2.shape[0]:
            diff_in_records.append(abs(df1.shape[0] - df2.shape[0]))
        else:
            df1 = df1.reset_index(drop=True)
            df2 = df2.reset_index(drop=True)
            diffs = df1.compare(df2, align_axis=1).shape[0]
            changes.append(diffs)

    if not diff_in_records and not sum(changes):
        return []

    tot_rec = len(unique_indices)
    rprt = [
        "     * Indices are not unique. Comparing per index",
        f"        * {tot_rec - (len(changes) + len(diff_in_records)):,} / {tot_rec :,} indices suffered no changes",
        f"        * {len(changes):,} / {tot_rec :,} indices have same size but suffered changes to fields",
        f"        * {len(diff_in_records):,} / {tot_rec :,} indices with different number of entries",
    ]
    if len(changes):
        rprt.append(f"        * Average number of records changed per unique index is {round(mean(changes), 5)}")
    if len(diff_in_records):
        rprt.append(f"        * {round(mean(diff_in_records), 5)} is the average number in entries for these indices")
    return rprt
