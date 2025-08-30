# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

import pandas as pd

from .loc_park_base import LocParkBase


class Parking(LocParkBase):
    def __init__(self, element_id: int, geotool, data_tables, conn=None, data=None):
        dt = pd.DataFrame([]) if data is None else data
        super().__init__(element_id, "Parking", geotool, data_tables, dt, conn)
        self.parking = element_id

    def __lt__(self, other):
        return self.space < other.space
