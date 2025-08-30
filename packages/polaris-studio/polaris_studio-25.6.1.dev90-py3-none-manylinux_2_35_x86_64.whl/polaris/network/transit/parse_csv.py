# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import copy
import csv
from io import TextIOWrapper
from typing import Optional

import numpy as np
from numpy.lib.recfunctions import append_fields


# Copied from AequilibraE


def parse_csv(file_name: str, column_order: Optional[dict] = None):
    tot = []

    col_order = column_order or {}
    if isinstance(file_name, str):
        csvfile = open(file_name, encoding="utf-8-sig")
    else:
        csvfile = TextIOWrapper(file_name, encoding="utf-8-sig")

    contents = csv.reader(csvfile, delimiter=",", quotechar='"')
    numcols = 0
    for row in contents:
        if not len("".join(row).strip()):
            continue
        broken = [x.encode("ascii", errors="ignore").decode().strip() for x in row]

        if not numcols:
            numcols = len(broken)
        else:
            if numcols < len(broken):
                broken.extend([""] * (numcols - len(broken)))

        tot.append(broken)
    titles = tot.pop(0)
    csvfile.close()
    if tot:
        data = np.core.records.fromrecords(tot, names=[x.lower() for x in titles])  # type: ignore
    else:
        return empty()

    missing_cols_names = [x for x in col_order.keys() if x not in data.dtype.names]
    for col in missing_cols_names:
        data = append_fields(data, col, np.array([""] * len(tot)))

    if col_order:
        col_names = [x for x in col_order.keys() if x in data.dtype.names]
        data = data[col_names]

        # Define sizes for the string variables
        col_order = copy.deepcopy(col_order)
        for c in col_names:
            if col_order[c] is str:
                col_order[c] = object
            else:
                if data[c].dtype.char.upper() in ["U", "S"]:
                    data[c][data[c] == ""] = "0"

        new_data_dt = [(f, col_order[f]) for f in col_names]

        if int(data.shape.__len__()) > 0:
            return np.array(data, new_data_dt)
        else:
            return data
    else:
        return data


class empty:
    shape = [0]
