# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from sqlite3 import Connection
from typing import List

import geopandas as gpd
import pandas as pd

from .loc_park_base import LocParkBase
from .location_links import loc_link_candidates, location_links_builder
from .parking import Parking


class Location(LocParkBase):
    _expanding_factor = 1.1

    def __init__(self, element_id: int, geotool, data_tables, conn, data=None):
        dt = pd.DataFrame([]) if data is None else data
        super().__init__(element_id, "Location", geotool, data_tables, dt, conn)
        self.land_use: str
        self.location = element_id

    def update_location_links(self, conn: Connection, maximum_distance=2000, multiple=True, clear=True) -> None:
        """Updates the Location_Links records with links that correspond to this location.

        Only the link associated with the Location in the location table is placed in the Location_Links table.
        All other records for that location are cleared out.

        Args:
            *maximum_distance* (:obj:`float`): Maximum distance for which a link can be connected to a location (excludes closest link)

            *multiple_links* (:obj:`bool`): Connects each location to multiple links in the same block if True
            and only to the nearest link if false. Defaults to True

            *clear* (:obj:`bool`): If True, clears all records in the Location_Links table for this location. Defaults to True
        """

        if clear:
            conn.execute("Delete from Location_links where location=?", [int(self.location)])
            conn.commit()
        if not multiple or self.geo is None:
            self.update_link(save=True, conn=conn)
            sql = """INSERT INTO Location_Links (location, link, distance)
                                     SELECT location, link, setback from Location where location=?"""
            conn.execute(sql, [int(self.location)])
            conn.commit()
            return

        links = self._create_multiple_location_links(maximum_distance)
        sql = "Insert into Location_Links(location, link, distance) VALUES (?,?,0)"
        conn.executemany(sql, links)
        conn.commit()

    def _create_multiple_location_links(self, maximum_distance: float) -> list:
        links_layer = self.geotool.get_geo_layer("link")[["link", "use_codes", "type", "geo"]]
        locs = gpd.GeoDataFrame(
            pd.DataFrame({"location": [self.id], "land_use": self.land_use}), geometry=[self.geo], crs=links_layer.crs
        )

        loc_links = loc_link_candidates(locs, links_layer, maximum_distance)
        if loc_links.empty:
            return []
        return location_links_builder(loc_links).to_records(index=False)

    def add_parking(self, conn: Connection, parkings: List[Parking]) -> None:
        """Adds a parking facility to the location by adding a record to Location_Parking"""
        conn.execute("DELETE FROM Location_Parking where location=?", [self.location])
        sql = "INSERT INTO Location_Parking(location, parking, distance, id) VALUES (?,?,?,0)"
        # The distance is computed by a trigger
        data = [[int(self.location), int(park.parking), 0] for park in parkings]
        conn.executemany(sql, data)
        conn.commit()
