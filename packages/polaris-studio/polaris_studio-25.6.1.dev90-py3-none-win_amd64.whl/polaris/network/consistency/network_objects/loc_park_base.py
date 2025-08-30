# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from typing import Optional

import pandas as pd

from .data_record import DataRecord


class LocParkBase(DataRecord):
    def __init__(
        self, element_id: int, table_name, geotool, data_table, data: pd.DataFrame, conn: Optional[sqlite3.Connection]
    ):
        self.dir: int
        self.setback: float
        self.link: int
        self.offset: float
        super().__init__(element_id, table_name, data_table, data, conn)
        from polaris.network.tools.geo import Geo

        self.geotool: Geo = geotool
        self.link_corrected = False

    def update_link(self, conn: sqlite3.Connection, force_update=False, save=True):
        """Update the link and offset to this Point (Location or Parking)

        Setback is computed automatically through triggers

        Args:
            *force_update* (:obj:`bool`, optional ): Re-computes offset even the if the current link
            info is correct. Defaults to False
            *save* (:obj:`bool`, optional ): Saves it to the database after re-computation. Defaults to True
        """

        new_link = self.geotool.get_link_for_point_by_mode(self.geo, ["AUTO"])
        if new_link == self.link and not force_update:
            return
        ofst = self.geotool.offset_for_point_on_link(new_link, self.geo)
        if [new_link, round(ofst, 2)] != [self.link, round(self.offset, 2)]:
            self.link_corrected = True
            self.link, self.offset = new_link, ofst
            if save:
                self.save(conn=conn)
