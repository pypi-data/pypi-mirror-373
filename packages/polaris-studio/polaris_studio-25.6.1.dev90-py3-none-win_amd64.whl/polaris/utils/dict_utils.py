# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import copy


def merge_dicts(*a, fn=None):
    x = copy.copy(a[0])
    for e in a[1:]:
        dup_keys = e.keys() & x.keys()
        new_keys = e.keys() - x.keys()
        for n in new_keys:
            x[n] = e[n]
        for n in dup_keys:
            if fn:
                x[n] = fn(x[n], e[n])
            else:
                x[n] = e[n]
    return x


def df_to_dict(df, col_from, col_to):
    return df[[col_from, col_to]].set_index(col_from).to_dict()[col_to]


def denest_dict(d: dict) -> dict:
    return {f"{k1}-{k2}": value for k1, inner_dict in d.items() for k2, value in inner_dict.items()}
