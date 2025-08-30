# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
def find_directions(angle: float) -> str:
    if angle < 45 or angle > 315:
        return "SB"
    if 45 <= angle < 135:
        return "WB"
    if 135 <= angle < 225:
        return "NB"
    return "EB"
