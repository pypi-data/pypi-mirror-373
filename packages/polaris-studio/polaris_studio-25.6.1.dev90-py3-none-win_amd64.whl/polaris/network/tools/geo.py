# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from typing import Dict, Optional, Any, Union, List

import geopandas as gpd
import requests
import shapely.wkb
from pyproj import Transformer
from shapely import Geometry
from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.ops import unary_union

from polaris.utils.database import data_table_access
from polaris.network.tools.geo_index import GeoIndex
from polaris.network.traffic.hand_of_driving import get_driving_side
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import read_and_close
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.structure_finder import find_table_index


class Geo:
    """Suite of generic geo-operations commonly used across other Polaris_Network submodules

    Changing the computation parameters is as simple as editing the dictionary **Geo.parameters**"""

    def __init__(self, network_file: os.PathLike):
        self.geo_idx: Dict[str, GeoIndex] = {}
        self._outside_zones = 0
        self.graphs: Dict[str, Any] = {}
        self.geo_objects: Dict[str, Any] = {}
        self.__model_area = None

        polaris_logging()
        self.map_matching: Dict[str, Union[int, float]] = {
            "links_to_search": 20,
            "bearing_tolerance": 22.5,
            "buffer_size": 32,
        }
        self._network_file = network_file
        self.__srid: Optional[int] = None
        self.__transformer: Optional[Any] = None
        self.__layers: Dict[str, Any] = {}
        self.__driving_side: Optional[int] = None

    @property
    def conn(self) -> int:
        raise Exception("NO CONNECTION HERE")

    @property
    def srid(self) -> int:
        if self.__srid is None:
            self.__srid = get_srid(database_path=self._network_file)
        return self.__srid

    @property
    def transformer(self):
        if self.__transformer is None:
            self.__transformer = Transformer.from_crs(f"epsg:{self.srid}", "epsg:4326", always_xy=True)
        return self.__transformer

    def clear_cache(self) -> None:
        """Eliminates all data available on cache"""
        self.geo_idx.clear()
        self._outside_zones = 0
        self.graphs.clear()

    def get_timezone(self):
        """Returns the time-zone for the current model. Uses the centroid of the model area as defined by the zoning
        layer"""
        poly = self.model_area
        lon, lat = self.transformer.transform(poly.centroid.xy[0][0], poly.centroid.xy[1][0])

        url = f"http://api.geonames.org/timezoneJSON?formatted=true&lat={lat}&lng={lon}&username=pveigadecamargo"
        r = requests.get(url)
        if r.status_code != 200:
            logging.warning(f"Could not retrieve timezone information from {url}., Returning GMT")
            return "Etc/GMT"
        return r.json()["timezoneId"]

    def get_geo_item(self, layer: str, geo: Geometry) -> int:
        """Get the closest feature from *layer* to a given geometry *geo

        Args:
            *layer* (:obj:`str`): The name of the layer we are looking for
            *point* (:obj:`Point`): A Shapely Point object

        Return:
            *element* (:obj:`int`): Element ID
        """
        if layer.lower() == "location":
            return self.__get_closest_for_layer(geo, "Location", "location")

        elif layer.lower() in ["transit_bike", "bike_link"]:
            return self.__get_closest_for_layer(geo, "Transit_Bike", "bike_link")

        elif layer.lower() in ["transit_walk", "walk_link"]:
            return self.__get_closest_for_layer(geo, "Transit_Walk", "walk_link")

        elif layer.lower() == "zone":
            return self.__get_closest_for_layer(geo, "zone", "zone")

        elif layer.lower() == "link":
            return self.__get_closest_for_layer(geo, "Link", "link")

        elif layer.lower() == "node":
            return self.__get_closest_for_layer(geo, "Node", "node")

        else:
            raise ValueError(f"Layer {layer} name not recognized")

    def get_geo_for_id(self, layer: str, id: int) -> Union[Point, LineString, Polygon]:
        """Get the feature from *layer* with the given identifier (id)

        Args:
            *layer* (:obj:`str`): The name of the layer we are looking for
            *id* (:obj:`int`): The unique identifier of the object

        Return:
            *Shapely geometry* (:obj:`geometry`): Geometry for feature with ID *id* in layer *layer*
        """
        lyr = self.get_geo_layer(layer)  # type: gpd.GeoDataFrame
        with read_and_close(self._network_file, spatial=True) as conn:
            idx = find_table_index(conn, layer)
        return lyr.loc[lyr[idx] == id, "geo"].values[0]  # type: ignore

    def get_parkings(self, geometry: Union[Point, LineString, Polygon], max_distance: float) -> List[int]:
        """Get the list of Parking facilities within a certain distance from the provided geometry

        Args:
            *geometry* (:obj:`Union[Point, LineString, Polygon]`): A Shapely Geometry object
            *max_distance* (:obj:`int`): Maximum distance for a certain parking_id

        Return:
            *parkings* (:obj:`List[int]`): List of Parking IDs
        """

        lyr = self.get_geo_layer("parking")
        idx = lyr.sindex  # type: shapely.STRtree

        closest = idx.query(geometry, predicate="dwithin", distance=max_distance)
        return [
            lyr.at[x, "parking"]
            for x in closest
            if isinstance(geometry, Point) or lyr.at[x, "geo"].distance(geometry) < max_distance
        ]

    def get_link_for_point_by_mode(self, point: Point, mode: Union[str, list]) -> int:
        """Analyzes the network in search of links (of an specific mode) closest to a given point

        The number of link candidates to retrieve from the spatial index analysis is defined by the
        parameter *links_to_search* in the map_matching parameter dictionary.

        Args:

            *point* (:obj:`Point`): Point for which we want to find closest link in the network
            *mode* (:obj:`str` or :obj:`list`): Mode (or modes) to consider when searching. When a list of modes is
                                                is provided, only links that allow ALL modes are considered

        Returns:

            *link ID* (:obj:`int`): link ID found near point geometry
        """

        # parameters
        # Before grabbing the filtered layer, we need to create it.
        # There is no generic way to build a filtered layer, so we rely on the "side-effect" of retrieving it
        _ = self.get_link_layer_by_mode(mode)
        return self.__get_closest_for_layer(point, f"link_{self._mode_name(mode)}", "link")

    def get_link_layer_by_mode(self, mode: Union[str, list]) -> gpd.GeoDataFrame:
        """Gets the link layer for a certain mode. If not ready, builds it
        Args:
            *mode* (:obj:`str` or :obj:`list`): Mode (or modes) to consider when searching. When a list of modes is
                                                is provided, only links that allow ALL modes are considered
        Returns:
            *layer* (:obj:`gpd.GeoDataFrame`): Filtered link layer
        """

        # parameters
        modename = self._mode_name(mode)

        modes = mode if isinstance(mode, list) else [mode]
        self.__build_filtered_layer("link", "use_codes", modes, f"link_{modename}")
        return self.__layers[f"link_{modename}"]

    def offset_for_point_on_link(self, link: int, point: Point) -> float:
        """
            Given a link ID and a Point, this method computes the offset of point

            It takes flow directionality (ab/ba lanes) in consideration when computing if the link
            will be accessed in one direction or another

        Args:

            *link* (:obj:`int`): Link ID to compute offset for
            *point* (:obj:`Point`): Point object to compute offset for

        Returns
            *offset* (:obj:`float`): Distance along a link a node is located in
        """

        links = self.get_geo_layer("link")  # type: gpd.GeoDataFrame

        link_ = links.loc[links.link == link, :]
        link_geo = link_.geo.values[0]
        lanes_ab = link_.lanes_ab.values[0]
        lanes_ba = link_.lanes_ba.values[0]

        tot_len = link_geo.length
        projected = link_geo.project(point)

        dist_from_a, dist_from_b = round(projected, 8), round(tot_len - projected, 8)
        # If either of the lanes vars are zero - we know we want the other side
        if lanes_ab == 0:
            return dist_from_b
        elif lanes_ba == 0:
            return dist_from_a

        # Otherwise we have to see which side of the road the point lies on
        side = self.determine_side_of_line(Point(link_geo.coords[0]), Point(link_geo.coords[-1]), point)

        # Handle different driving sides
        if self._driving_side == -1:
            return dist_from_b if side == "right" else dist_from_a
        else:
            return dist_from_a if side == "right" else dist_from_b

    def side_of_link_for_point(self, point: Point, link: Union[int, LineString]) -> int:
        """Computes the side of the link a point is with relationship to a line

        Args:

            *link* (:obj:`int`): Link ID of the link in question
            *point* (:obj:`Point`): Geometry of the point we are interested in
        Returns
            *side* (:obj:`int`): 0 for right side and 1 for left

        """
        link_geo = self.get_geo_for_id("link", link) if isinstance(link, int) else link
        side = self.determine_side_of_line(Point(link_geo.coords[0]), Point(link_geo.coords[-1]), point)
        return 0 if side == "right" else 1

    def _mode_name(self, mode: Union[list, str]) -> str:
        if isinstance(mode, str):
            return mode
        return "|".join(mode)

    def convex_hull(self):
        with read_and_close(self._network_file, spatial=True) as conn:
            curr = conn.execute("select AsBinary(geo) from Link where ST_Length(geo) > 0;")
            links = [shapely.wkb.loads(x[0]) for x in curr.fetchall()]
        return unary_union(links).convex_hull

    @property
    def model_area(self) -> Union[MultiPolygon, Polygon]:
        """Returns the modelling are as the union of all zones as a single MultiPolygon"""
        return self.__model_area or self.__build_model_area()

    def clear_layers(self):
        self.__layers.clear()

    def add_layer(self, layer, layer_name: str):
        # This function is needed for QPolaris
        self.__layers[layer_name] = layer

    def get_geo_layer(self, layer_name: str) -> gpd.GeoDataFrame:
        if layer_name in self.__layers:
            return self.__layers[layer_name]

        layer = data_table_access.DataTableAccess(self._network_file).get(layer_name)
        if layer_name.lower() == "link":
            lt = data_table_access.DataTableAccess(self._network_file).get("Link_type")
            layer = layer.merge(lt, left_on="type", right_on="link_type", how="left")
        self.__layers[layer_name] = layer
        return self.__layers[layer_name]

    def __build_filtered_layer(self, layer_name: str, field: str, filter_values: list, store_name: str):
        if store_name in self.__layers:
            return
        layer = self.get_geo_layer(layer_name)

        for filter_value in filter_values:
            layer = layer[layer[field].str.contains(str(filter_value))]

        self.__layers[store_name] = layer.reset_index(drop=True)

    def __build_model_area(self):
        with read_and_close(self._network_file, spatial=True) as conn:
            wkb = conn.execute("select AsBinary(ST_Union(geo)) from zone").fetchone()[0]
        # We check if we can get the model area from
        #  the union or zones. If no zones available, we
        #  estimate it from the convex hull of all links
        if wkb is not None:
            self.__model_area = shapely.wkb.loads(wkb)
        else:
            self.__model_area = self.convex_hull()

        self.__model_area = self.__model_area.buffer(100).buffer(-100)
        return self.__model_area

    def __get_closest_for_layer(self, geometry: Geometry, layer: str, field: str) -> int:
        lyr = self.get_geo_layer(layer)  # type: gpd.GeoDataFrame

        if lyr.empty:
            return None  # type: ignore

        idx = lyr.sindex  # type: shapely.strtree.STRtree

        closest = idx.nearest(geometry, return_distance=False, return_all=False)[1][0]
        return lyr.at[closest, field]

    def _set_srid(self, srid: int) -> None:
        self.__srid = srid

    @property
    def _driving_side(self):
        if self.__driving_side is None:
            self.__driving_side = get_driving_side(database_path=self._network_file)
        return self.__driving_side

    @staticmethod
    def determine_side_of_line(line_start: Point, line_end: Point, point: Point) -> str:
        line_vector = (line_end.x - line_start.x, line_end.y - line_start.y)
        point_vector = (point.x - line_start.x, point.y - line_start.y)
        cross_product = line_vector[0] * point_vector[1] - line_vector[1] * point_vector[0]

        # Determine the side
        if cross_product > 0:
            return "left"
        elif cross_product < 0:
            return "right"
        else:
            return "line"
