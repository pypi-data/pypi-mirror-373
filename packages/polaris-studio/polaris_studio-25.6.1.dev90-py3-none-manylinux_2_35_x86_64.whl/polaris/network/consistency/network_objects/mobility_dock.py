# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3

import pandas as pd

from .data_record import DataRecord


class MicromobilityDock(DataRecord):
    def __init__(self, element_id, data_tables, geotool, conn=None):
        super(MicromobilityDock, self).__init__(element_id, "Micromobility_Docks", data_tables, pd.DataFrame(), conn)
        self.geotool = geotool  # type: polaris.network.tools.geo.Geo
        if self.geo:
            self.box = self.geo.bounds

    def save(self, conn: sqlite3.Connection):
        super(MicromobilityDock, self).save(conn)
        self._data.refresh_cache("mobility_docks")

    def update_zone(self, conn=None, commit=True):
        self.zone = self.geotool.get_geo_item("zone", self.geo)

        if commit:
            self.save(conn)

    def update_link(self, conn=None, commit=True):
        self.link = self.geotool.get_link_for_point_by_mode(self.geo, ["AUTO"])
        self.offset = self.geotool.offset_for_point_on_link(self.link, self.geo)
        self.setback = self.geotool.get_geo_for_id("link", self.link).distance(self.geo)
        self.dir = self.geotool.side_of_link_for_point(link=self.link, point=self.geo)

        if commit:
            self.save(conn)
