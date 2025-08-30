# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from sqlite3 import Connection

from polaris.network.constants import constants, WALK_AGENCY_ID
from polaris.network.transit.transit_elements.basic_element import BasicPTElement
from polaris.utils.database.db_utils import read_and_close


class Agency(BasicPTElement):
    """Transit Agency to load into the database

    :Database class members:

    * agency_id (:obj:`int`): ID for the transit agency
    * agency (:obj:`str`): Name of the transit agency
    * feed_date (:obj:`str`): Date for the transit feed using in the import
    * service_date (:obj:`str`): Date for the route services being imported
    * description (:obj:`str`): Description of the feed"""

    def __init__(self, network_file: PathLike):
        self.agency = ""
        self.feed_date = ""
        self.service_date = ""
        self.description = 0
        self.__network_file = network_file
        self.agency_id = self.__get_agency_id()

    def save_to_database(self, conn: Connection) -> None:
        """Saves route to the database"""

        data = [self.agency_id, self.agency, self.feed_date, self.service_date, self.description]
        sql = """insert into Transit_Agencies (agency_id, agency, feed_date, service_date, description)
                 values (?, ?, ?, ?, ?);"""
        conn.execute(sql, data)
        conn.commit()

    def __get_agency_id(self):
        with read_and_close(self.__network_file) as conn:
            sql = "Select max(coalesce(agency_id, ?), ?) from Transit_Agencies;"
            data = conn.execute(sql, [WALK_AGENCY_ID + 1, WALK_AGENCY_ID + 1]).fetchone() or [WALK_AGENCY_ID + 1]
        c = constants()
        c.agencies["agencies"] = max(c.agencies.get("agencies", 1) + 1, data[0])
        return c.agencies["agencies"]
