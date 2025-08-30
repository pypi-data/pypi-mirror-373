# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md


def clamp(v, lo, hi):
    """Named to match the equivalent cpp function.
    If the value of v is within [lo, hi], returns v; otherwise returns the nearest boundary.
    """
    return lo if v < lo else hi if v > hi else v
