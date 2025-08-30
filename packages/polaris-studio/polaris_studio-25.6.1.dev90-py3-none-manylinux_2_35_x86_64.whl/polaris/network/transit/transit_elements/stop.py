# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from sqlite3 import Connection
from typing import Dict, Any, Optional

import shapely.wkb
from shapely.geometry import Point

from polaris.network.constants import constants, AGENCY_MULTIPLIER
from polaris.network.utils.srid import get_srid
from polaris.network.transit.transit_elements.basic_element import BasicPTElement


class Stop(BasicPTElement):
    """Transit stop as read from the GTFS feed

    :GTFS class members:

    * stop (:obj:`str`): Stop corresponds to stop_id as read from the GTFS feed prefixed with the agency ID prefix
    * stop_code (:obj:`str`): Stop code as read from the GTFS feed
    * stop_name (:obj:`str`): Stop name as read from the GTFS feed
    * stop_desc (:obj:`str`): Stop description as read from the GTFS feed
    * stop_lat (:obj:`float`): Stop latitude as read from the GTFS feed
    * stop_lon (:obj:`float`): Stop longitude as read from the GTFS feed
    * stop_street (:obj:`str`): Stop street as read from the GTFS feed
    * zone_id (:obj:`str`): Transit Zone ID as read from the GTFS feed
    * stop_url (:obj:`str`): Stop URL as read from the GTFS feed
    * location_type (:obj:`int`): Stop location type as read from the GTFS feed
    * parent_station (:obj:`str`): Stop parent station as read from the GTFS feed
    * stop_timezone (:obj:`str`): Stop Time Zone as read from the GTFS feed
    * wheelchair_boarding (:obj:`int`): Stop wheelchair boarding flag as read from the GTFS feed

    :Processing class members:

    * stop_id (:obj:`int`): Stop ID is a integer that will be used as the unique identifier for the stop in the database
    * stop (:obj:`str`): Stop ID as read from the GTFS feed prefixed with the agency ID prefix
    * taz (:obj:`str`): Model Zone number (geo-tagged)
    * agency (:obj:`str`): Agency name
    * has_parking (:obj:`int`): Flag to identify if stop has parking available
    * srid (:obj:`int`): Database SRID
    * geo (:obj:`Point`): Point object corresponding to the provided Latitude/Longitude
    * route_type (:obj:`int`): Route type of the routes associated with this stop

    """

    def __init__(self, agency_id: int):
        self.stop_id = -1
        self.stop = ""
        self.stop_code = ""
        self.stop_name = ""
        self.stop_desc = ""
        self.stop_lat = 0.0
        self.stop_lon = 0.0
        self.stop_street = ""
        self.zone = ""
        self.zone_id: Optional[int] = None
        self.stop_url = ""
        self.location_type = 0
        self.parent_station = ""
        self.stop_timezone = ""
        self.wheelchair_boarding = 0

        # Not part of GTFS
        self.taz: Optional[int] = None
        self.agency = ""
        self.agency_id = agency_id
        self.has_parking = 0
        self.srid = -1
        self.geo = Point()
        self.route_type: Optional[int] = None
        self.___map_matching_id__: Dict[Any, Any] = {}
        self.__moved_map_matching__ = 0

    def populate(self, record: tuple, headers: list) -> None:
        for key, value in zip(headers, record):
            if key not in self.__dict__.keys():
                logging.error(f"{key} field in Stops.txt is unknown field for that file on GTFS. Ignoring it.")
                continue

            key = key if key != "stop_id" else "stop"
            key = key if key != "zone_id" else "zone"
            value = int(value) if key == "route_type" else value
            self.__dict__[key] = value

        if None not in [self.stop_lon, self.stop_lat]:
            self.geo = Point(self.stop_lon, self.stop_lat)
        if len(str(self.zone_id)) == 0:
            self.zone_id = None

    def save_to_database(self, conn: Connection, commit=True):
        """Saves Transit Stop to the database"""

        sql = """insert into TRANSIT_STOPS (stop_id, stop, agency_id, X, Y, Z, name,
                                            parent_station, description, street, zone, transit_zone_id, has_parking,
                                            route_type, moved_by_matching, geo)
                 values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GeomFromWKB(?, ?));"""

        dt = self.data
        conn.execute(sql, dt)
        if commit:
            conn.commit()

    def from_database(self, conn: Connection, stop_id):
        sql = """SELECT stop_id,
                        stop,
                        agency_id,
                        X,
                        Y,
                        name,
                        parent_station,
                        description,
                        street, zone, transit_zone_id, has_parking, route_type, moved_by_matching, ST_AsBinary(geo)
                 FROM Transit_Stops
                 WHERE stop_id=?"""
        data = conn.execute(sql, [stop_id]).fetchone()
        (
            self.stop_id,
            self.stop,
            self.agency_id,
            self.stop_lon,
            self.stop_lat,
            self.stop_name,
            self.parent_station,
            self.stop_desc,
            self.stop_street,
            self.taz,
            self.zone_id,
            self.has_parking,
            self.route_type,
            self.__moved_map_matching__,
            self.geo,
        ) = data
        self.geo = shapely.wkb.loads(self.geo)
        self.srid = get_srid(conn=conn)
        return self

    @property
    def data(self) -> list:
        return [
            self.stop_id,
            self.stop,
            self.agency_id,
            self.stop_lon,
            self.stop_lat,
            0,
            self.stop_name,
            self.parent_station,
            self.stop_desc,
            self.stop_street,
            self.taz,
            self.zone_id,
            self.has_parking,
            self.route_type,
            self.__moved_map_matching__,
            self.geo.wkb,
            self.srid,
        ]

    def get_node_id(self):
        c = constants()

        val = 1 + c.stops.get(self.agency_id, AGENCY_MULTIPLIER * self.agency_id)
        c.stops[self.agency_id] = val
        self.stop_id = c.stops[self.agency_id]
