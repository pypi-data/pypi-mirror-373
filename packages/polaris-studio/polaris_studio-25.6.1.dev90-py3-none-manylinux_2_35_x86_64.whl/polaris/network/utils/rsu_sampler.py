# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import random
from textwrap import dedent

from polaris.utils.database.db_utils import commit_and_close


class RsuSampler:
    """Class to add random RSU to a supply network."""

    def __init__(self, supply_db, highway_links_pr=None, major_pr=None, minor_pr=None, local_pr=None):
        self.supply_db = supply_db
        self.highway_links_pr = highway_links_pr or 0.125
        self.major_pr = major_pr or 0.125
        self.minor_pr = minor_pr or 0.0
        self.local_pr = local_pr or 0.0
        self._link_records = {}
        self._highway_links = {}
        self._major_links = {}
        self._minor_links = {}
        self._local_links = {}

        self.load_links()

    def generate_links_with_rsu_and_push(self):
        def sample(a_list, proportion):
            return random.sample(list(a_list), int(proportion * len(a_list)))

        all_links = (
            sample(self._highway_links.keys(), self.highway_links_pr)
            + sample(self._major_links.keys(), self.major_pr)
            + sample(self._minor_links.keys(), self.minor_pr)
            + sample(self._local_links.keys(), self.local_pr)
        )

        def fn(link_id):
            if self._link_records[link_id]["lanes_ab"] > 0:
                return link_id, 0
            if self._link_records[link_id]["lanes_ba"] > 0:
                return link_id, 1

        all_values = [fn(link_id) for link_id in all_links]
        all_values = [x for x in all_values if x]  # remove None values
        all_values = [(i + 1, lid, dirn, 0, 0, "TRAVEL_TIME", 0) for (i, (lid, dirn)) in enumerate(all_values)]

        if not all_values:
            return

        with commit_and_close(self.supply_db) as conn:
            conn.execute("DELETE from RoadSideUnit")
            sql = dedent(
                """
                INSERT into RoadSideUnit (unit_id, link, dir, position, power,
                                          collected_info, logging_interval_seconds)
                VALUES (?,?,?,?,?,?,?);"""
            )
            conn.executemany(sql, all_values)

    def load_links(self):
        with commit_and_close((self.supply_db)) as conn:
            query = "SELECT link, type, lanes_ab, lanes_ba from link"

            for link, tp, lanes_ab, lanes_ba in conn.execute(query):
                self._link_records[link] = {"link": link, "type": tp, "lanes_ab": lanes_ab, "lanes_ba": lanes_ba}
        self.classify_links()

    def classify_links(self):
        for link in self._link_records:
            if self._link_records[link]["type"] == "COLLECTOR" or self._link_records[link]["type"] == "LOCAL":
                self._local_links[link] = self._link_records[link]
            elif self._link_records[link]["type"] == "EXPRESSWAY" or self._link_records[link]["type"] == "RAMP":
                self._highway_links[link] = self._link_records[link]
            elif self._link_records[link]["type"] == "MAJOR":
                self._major_links[link] = self._link_records[link]
            elif self._link_records[link]["type"] == "MINOR":
                self._minor_links[link] = self._link_records[link]
