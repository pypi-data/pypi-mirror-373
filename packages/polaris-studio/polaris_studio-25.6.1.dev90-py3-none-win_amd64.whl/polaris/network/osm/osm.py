# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import datetime
import hashlib
import logging
import os
import warnings
from math import sqrt, ceil
from time import sleep
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd
from shapely.geometry import box

from polaris.network.constants import OSM_NODE_RANGE
from polaris.network.osm.osm_utils import start_cache
from polaris.network.osm.traffic_light import TrafficLight
from polaris.network.starts_logging import logger
from polaris.network.tools.geo_index import GeoIndex
from polaris.network.utils.srid import get_srid
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.utils.database.db_utils import commit_and_close, read_and_close
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.user_configs import UserConfig


class OSM:
    """Suite of geo-operations to retrieve data from Open-Street Maps

    **FOR LARGE MODELLING AREAS IT IS RECOMMENDED TO DEPLOY YOUR OWN OVERPASS SERVER**

    ::

        from os.path import join
        import sqlite3
        from datetime import timedelta
        from polaris.network.network import Network

        root = 'D:/Argonne/GTFS/CHICAGO'
        network_path = join(root, 'chicago2018-Supply.sqlite')

        net = Network()
        net.open(network_path)

        osm = net.osm

        # The first call to osm.get_traffic_signal() will download data for
        # the entire modelling area

        # Here we default to our own server
        osm.url = 'http://192.168.0.105:12345/api'
        # And we also set the wait time between queries to zero,
        # as we are not afraid of launching a DoS attack on ourselves
        osm.sleep_time = 0

        # If we want to list all nodes in the network that have traffic lights
        # We can get the distance to the closest traffic signal on OSM, including their OSM ID

        for node, wkb in net.conn.execute('Select node, ST_asBinary(geo) from Node').fetchall():
            geo = shapely.wkb.loads(wkb)
            tl = osm.get_traffic_signal(geo)
            print(f'{node}, {tl.distance}, {tl.osm_id}'

        # A more common use is within the Intersection/signal API
        # We would ALSO assign the url and sleep time EXACTLY as shown above
        for node in net.conn.execute('Select node from Node').fetchall():
            intersection = net.get_intersection(node)

            if intersection.osm_signal():
                intersection.delete_signal():
                sig = intersection.create_signal()
                sig.re_compute()
                sig.save()

        # We can also retrieve all hotels in the modelling area
        hotels = osm.get_tag('tourism', 'hotel')

        # Or all hospitals
        hosp = osm.get_tag('healthcare', 'hospital')

        # Universities
        universities = osm.get_tag('amenity', 'university')

        # or schools
        schools = osm.get_tag('amenity', 'school')


    """

    #: URL of the Overpass API
    url = UserConfig().osm_url
    #: Pause between successive queries when assembling OSM dataset
    sleep_time = 1
    __tile_size = 500
    __cache_db = UserConfig().osm_cache

    def __init__(self, path_to_file: os.PathLike) -> None:
        from polaris.utils.database.data_table_access import DataTableAccess
        from polaris.network.tools.geo import Geo

        polaris_logging()
        self.srid = get_srid(database_path=path_to_file)
        self.__data_tables = DataTableAccess(path_to_file)
        self.__geotool = Geo(path_to_file)

        self.__traffic_lights = {}  # type: Dict[int, Any]

        self.links = {}  # type: Dict[int, Any]

        self.mode_link_idx: Dict[str, GeoIndex] = {}
        self._outside_zones = 0
        self.__osm_data: Dict[str, dict] = {}
        self.graphs: Dict[str, Any] = {}
        self.failed = True
        self._path_to_file = path_to_file
        self.__model_zones_polygon: Optional[Any] = None
        self.__model_boundaries: Optional[Any] = None

    def get_traffic_signal(self, point) -> TrafficLight:
        """Returns the traffic light object closest to the point provided

        Args:
            *point* (:obj:`Point`): A Shapely Point object

        Return:
            *traffic_light* (:obj:`TrafficLight`): Traffic light closest to the provided point
        """

        if self.__osm_data.get("highway", {}).get("traffic_signals", pd.DataFrame([])).empty:
            self.__load_traffic_light_data()

        tlight_gdf = self.__osm_data["highway"]["traffic_signals"]

        nearest_idx = list(tlight_gdf.sindex.nearest(point, return_all=False))[1][0]
        nearest_gdf = tlight_gdf.iloc[nearest_idx]

        t = TrafficLight()
        if not nearest_gdf.empty:
            t.distance = nearest_gdf.geo.distance(point)
            t.osm_id = nearest_gdf.osm_id
            t.geo = nearest_gdf.geo

        return t

    def get_amenities(self, amenity_type: str):
        """Finds all [amenities] (<https://wiki.openstreetmap.org/wiki/Key:amenity>) with a certain type for the
            model area.

        Args:
            *amenity_type* (:obj:`str`): The value for the OSM tag 'amenity'

        Return:
            *amenities* (:obj:`gpd.GeoDataFrame`): GeoDataframe with all amenities of the given type fond on OSM
        """
        queries = self.__tag_queries("amenity", amenity_type)

        return self.__load_osm_data(tag="amenity", tag_value=amenity_type, queries=queries)

    def get_tag(self, tag: str, tag_value: str):
        """Finds all instances where a [given tag] (<https://wiki.openstreetmap.org/wiki/Key:amenity>)
            has a certain value at OSM.

        Args:
            *tag* (:obj:`str`): The tag of interest for download
            *tag_value* (:obj:`str`): The value for the OSM tag chosen

        Return:
            *amenities* (:obj:`gpd.GeoDataFrame`): GeoDataframe with all selected tags of the given type fond on OSM
        """
        queries = self.__tag_queries(tag, tag_value)
        self.__load_osm_data(tag=tag, tag_value=tag_value, queries=queries)
        return self.__osm_data[tag][tag_value]

    def __tag_queries(self, tag: str, tag_value: str) -> List[str]:
        return [
            f'[out:json][timeout:180];(node["{tag}"="{tag_value}"]["area"!~"yes"]' + "({});>;);out;",
            f'[out:json][timeout:180];(way["{tag}"="{tag_value}"]["area"!~"yes"]' + "({});>;);out;",
        ]

    def conflate_osm_walk_network(self, tolerance=10):  # pragma: no cover
        """It moves the link ends from the OSM_WALK on top of nodes from the
        roadway whenever they are closer than the tolerance, while also
        re-populating node_a and node_b fields with values known to be unique
        and mutually consistent.
        Each node from the roadway network can only have one node from the
        OSM_WALK network moved on top of them in order to prevent links from the
        OSM_WALK network to have their start and end at the same node.
        Args:
            *tolerance* (:obj:`Float`): Maximum distance to move a link end
        """
        import shapely.wkb

        self.__data_tables.refresh_cache()

        network = self.__data_tables.get("OSM_WALK")
        network.geo = network.geo.apply(shapely.wkb.loads)

        net_nodes = self.__data_tables.get("Node")
        net_nodes.geo = net_nodes.geo.apply(shapely.wkb.loads)

        sql = """select link_id,
                        st_asbinary(startpoint(geo)) from_node, startpoint(geo) from_geo,
                        X(startpoint(geo)) from_x, Y(startpoint(geo)) from_y ,
                        st_asbinary(endpoint(geo)) to_node, endpoint(geo) to_geo,
                         X(endpoint(geo)) to_x, Y(endpoint(geo)) to_y
                        from OSM_Walk"""

        with commit_and_close(self._path_to_file, spatial=True) as conn:
            df = pd.read_sql(sql, conn)

            sindex_status = conn.execute("select CheckSpatialIndex('OSM_Walk', 'geo')").fetchone()[0]
            if sindex_status is None:
                conn.execute("SELECT CreateSpatialIndex( 'OSM_Walk' , 'geo' );")
                conn.commit()
                if conn.execute("select CheckSpatialIndex('OSM_Walk', 'geo')").fetchone()[0] is None:
                    raise ValueError("OSM_Walk has no spatial index and we were not able to add one")
            elif sindex_status == 1:
                pass
            elif sindex_status == 0:
                conn.execute('select RecoverSpatialIndex("OSM_Walk", "geo");')
                if conn.execute("select CheckSpatialIndex('OSM_Walk', 'geo')").fetchone()[0] == 0:
                    raise ValueError("OSM_Walk has a broken spatial index and we were not able to recover it")
            elif sindex_status == -1:
                warnings.warn("There is something weird with the OSM_Walk spatial index. Better check it")

            network = network.merge(df, on="link_id")

            df = network.drop_duplicates(subset=["from_x", "from_y"])[["from_x", "from_y", "from_geo", "from_node"]]
            df.columns = ["x", "y", "orig_geo", "wkb"]
            df2 = network.drop_duplicates(subset=["to_x", "to_y"])[["to_x", "to_y", "to_geo", "to_node"]]
            df2.columns = ["x", "y", "orig_geo", "wkb"]
            osm_nodes = pd.concat([df, df2]).drop_duplicates(subset=["x", "y"])
            osm_nodes = osm_nodes.assign(node_id=np.arange(osm_nodes.shape[0]) + OSM_NODE_RANGE)

            # We update the OSM_Walk network with the newly computed OSM node IDs
            sql = f"""update OSM_Walk set node_a=? WHERE
                            StartPoint(geo)=? AND
                            ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'OSM_Walk'
                                      AND search_frame = buffer(?, {tolerance}))"""

            sql2 = f"""update OSM_Walk set node_b=? WHERE
                            EndPoint(geo)=? AND
                            ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'OSM_Walk'
                                      AND search_frame = buffer(?, {tolerance}))"""

            aux = osm_nodes[["node_id", "orig_geo", "orig_geo"]]
            aux.columns = ["a", "b", "c"]
            aux = aux.to_records(index=False).tolist()

            conn.executemany(sql, aux)
            conn.executemany(sql2, aux)
            conn.commit()

            # Update node_a
            osm_nodes.drop(columns=["orig_geo"], inplace=True)
            osm_nodes.columns = ["from_x", "from_y", "point_geo", "node_id"]

            osm_nodes.point_geo = osm_nodes.point_geo.apply(shapely.wkb.loads)
            network = network.merge(osm_nodes, how="left", on=["from_x", "from_y"])
            network.loc[:, "node_a"] = network.node_id
            network.drop(columns=["node_id", "point_geo"], inplace=True)

            # update node_b
            osm_nodes.columns = ["to_x", "to_y", "point_geo", "node_id"]
            network = network.merge(osm_nodes, how="left", on=["to_x", "to_y"])
            network.loc[:, "node_b"] = network.node_id
            network.drop(columns=["node_id", "point_geo"], inplace=True)

            # Build an index for the existing OSM nodes
            walk_node_idx = GeoIndex()
            walk_node_geos = {}
            for _, record in osm_nodes.iterrows():
                walk_node_idx.insert(feature_id=record.node_id, geometry=record.point_geo)
                walk_node_geos[record.node_id] = record.point_geo

            # Search for node correspondences
            association = {}
            for idx, rec in net_nodes.iterrows():
                nearest_list = list(walk_node_idx.nearest(rec.geo, 10))
                for near in nearest_list:
                    near_geo = walk_node_geos[near]
                    dist = near_geo.distance(rec.geo)
                    if dist > tolerance:
                        break

                    # Is that OSM node even closer to some other node?
                    if idx == self.__geotool.get_geo_item("node", near_geo):
                        association[near] = idx
                        break

            # update link geometries
            sql = """update OSM_Walk set geo = SetStartPoint(geo, GeomFromWKB(?,?)), node_a=? WHERE
                            StartPoint(geo)=GeomFromWKB(?,?) AND
                            ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'OSM_Walk'
                                      AND search_frame = GeomFromWKB(?,?))"""

            sql2 = """update OSM_Walk set geo = SetEndPoint(geo, GeomFromWKB(?,?)), node_b=? WHERE
                            EndPoint(geo)=GeomFromWKB(?,?) AND
                            ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'OSM_Walk'
                                      AND search_frame = GeomFromWKB(?,?))"""

            data_tot = []
            for near, node_from_net in association.items():
                old_geo = walk_node_geos[near]
                new_geo = net_nodes.geo.at[node_from_net]
                data_tot.append([new_geo.wkb, self.srid, node_from_net, old_geo.wkb, self.srid, old_geo.wkb, self.srid])

            conn.executemany(sql, data_tot)
            conn.executemany(sql2, data_tot)
            conn.commit()
            conn.execute('select RecoverSpatialIndex("OSM_Walk", "geo");')

    def clear_disk_cache(self):
        """Clears the OSM cache on disk"""
        self.__cache_db.unlink(True)
        self.__osm_data.clear()
        self.__traffic_lights.clear()

    @property
    def model_boundaries(self):
        return self.__model_boundaries or self.__get_boundaries()

    def set_tile_size(self, tile_size: int):
        """The use of smaller values for *tile_size* is only recommended if queries are returning
        errors with the default value of 500.
        """
        self.__tile_size = tile_size

    def __load_osm_data(self, tag, tag_value, queries):
        """Loads data from OSM or cached to disk"""
        import requests
        from shapely.geometry import box

        self.failed = False

        start_cache(self.__cache_db)
        self.__model_area_strict()
        if self.__check_all_cached(tag, tag_value):
            self.__load_from_cache(tag, tag_value)
            return
        # We won't download any area bigger than 25km by 25km
        bboxes = self.__bounding_boxes()
        logging.info(f"Downloading OSM data. {len(bboxes)} bounding boxes for tag {tag}:{tag_value}.")
        headers = requests.utils.default_headers()
        headers.update({"Accept-Language": "en", "format": "json"})
        for bbox in bboxes:
            bbox_str = ",".join([str(round(x, 6)) for x in bbox])
            cache_name = self.__cache_name(bbox_str, tag, tag_value)

            if self.__check_partial_download_cache(cache_name):
                logging.info(f"Found download {cache_name} in cache, skipping download")
                continue
            logging.info(f"Downloading tile {cache_name} for tag {tag}:{tag_value} with bbox {bbox_str}")

            for query in queries:
                if len(bboxes) * len(queries) > 2:
                    sleep(self.sleep_time)
                dt = {"data": query.format(bbox_str)}
                response = requests.post(f"{self.url}/interpreter", data=dt, timeout=180, headers=headers, verify=False)
                if response.status_code != 200:
                    self.__osm_data[tag][tag_value] = pd.DataFrame([])
                    Warning("Could not download data")
                    logger.error(f"Could not download data for tag {tag}:{tag_value}")
                    self.failed = True
                    self.__osm_data[tag][tag_value] = pd.DataFrame([])
                    return

                # get the response size and the domain, log result
                json_data = response.json()
                if "elements" in json_data:
                    self.__ingest_json(json_data, tag, tag_value, cache_name)

            with commit_and_close(self.__cache_db, spatial=True) as conn:
                box_wkb = box(bbox[1], bbox[0], bbox[3], bbox[2]).wkb
                idx_data = [cache_name, datetime.date.today().isoformat(), tag, tag_value, box_wkb]
                conn.execute(
                    """INSERT OR IGNORE INTO osm_downloads (id, download_date, tag, tag_value, geo)
                                 VALUES (?, ?, ?, ?, GeomFromWKB(?, 4326))""",
                    idx_data,
                )

        self.__load_from_cache(tag, tag_value)

    def __check_partial_download_cache(self, cache_name):
        with read_and_close(self.__cache_db, spatial=False) as conn:
            data = conn.execute("SELECT count(*) FROM osm_downloads WHERE id = ?", (cache_name,)).fetchone()
            return sum(data) > 0

    def __check_all_cached(self, tag, tag_value) -> bool:
        downloaded = DataTableAccess(self.__cache_db).get("osm_downloads", from_cache_ok=False)
        downloaded = downloaded[(downloaded["tag"] == tag) & (downloaded["tag_value"] == tag_value)]
        downloaded = downloaded.clip(self.__model_zones_polygon)

        if downloaded.empty or downloaded.geo.area.sum() / self.__model_zones_polygon.area < 0.999:  # type: ignore
            return False
            # Tiny (0.1%) slivers missing are not enough to consider the download invalid
        return True

    def __load_from_cache(self, tag, tag_value):
        data = DataTableAccess(self.__cache_db).get("osm_elements", from_cache_ok=False)
        data = data[(data["tag"] == tag) & (data["tag_value"] == tag_value)]
        self.__osm_data[tag] = {tag_value: data.clip(self.__model_zones_polygon).to_crs(self.srid)}

    def __ingest_json(self, json_data, tag, tag_value, cache_name):
        elements = json_data["elements"]
        node_index = {x["id"]: [x["lon"], x["lat"]] for x in elements if x.get("type", {}) == "node"}
        data = []
        for x in elements:
            id = x.get("id", None)
            if x.get("tags", {}).get(tag, "") != tag_value or id is None:
                continue
            all_tags = str(x.get("tags", "{}"))
            if "lon" not in x and "nodes" in x:
                lons = []
                lats = []
                # We get the geo-center of the points
                for nid in x["nodes"]:
                    if nid not in node_index:
                        continue
                    lons.append(node_index[nid][0])
                    lats.append(node_index[nid][1])
                lon = sum(lons) / max(len(lons), 1)
                lat = sum(lats) / max(len(lats), 1)
            else:
                lon = x.get("lon", 0)
                lat = x.get("lat", 0)

            data.append([id, lon, lat, tag, tag_value, all_tags])
        df = pd.DataFrame(data, columns=["osm_id", "x", "y", "tag", "tag_value", "all_tags"])
        if df.empty:
            return

        with commit_and_close(self.__cache_db, spatial=True) as conn:
            df = df.assign(lat=df.y, lon=df.x, download_id=cache_name)
            rec_data = df[["osm_id", "lon", "lat", "tag", "tag_value", "all_tags", "download_id", "x", "y"]].to_records(
                index=False
            )
            conn.executemany(
                """INSERT OR IGNORE INTO osm_elements (osm_id, x, y, tag, tag_value, all_tags, download_id, geo)
                                         VALUES (?, ?, ?, ?, ?, ?, ?, MakePoint(?, ?, 4326))""",
                rec_data,
            )

    def __bounding_boxes(self):
        parts = ceil(sqrt(self.model_boundaries.area / (self.__tile_size * self.__tile_size * 1000 * 1000)))
        area_bounds = list(self.model_boundaries.bounds)
        area_bounds[1], area_bounds[0] = self.__reverse_transformer.transform(area_bounds[0], area_bounds[1])
        area_bounds[3], area_bounds[2] = self.__reverse_transformer.transform(area_bounds[2], area_bounds[3])
        if parts == 1:
            bboxes = [area_bounds]
        else:
            bboxes = []
            xmin, ymin, xmax, ymax = area_bounds
            ymin_global = ymin
            delta_x = (xmax - xmin) / parts
            delta_y = (ymax - ymin) / parts
            for _ in range(parts):
                xmax = xmin + delta_x
                for _ in range(parts):
                    ymax = ymin + delta_y
                    bbox = [xmin, ymin, xmax, ymax]
                    if box(bbox[1], bbox[0], bbox[3], bbox[2]).intersects(self.__model_zones_polygon):
                        bboxes.append(bbox)
                    ymin = ymax
                xmin = xmax
                ymin = ymin_global
        return bboxes

    def __model_area_strict(self):
        self.__model_zones_polygon = self.__data_tables.get("Zone").to_crs(4326).union_all()

    def __load_traffic_light_data(self):

        # We build the spatial index with the traffic lights from OSM
        queries = ['[out:json][timeout:180];(node["highway"="traffic_signals"]["area"!~"yes"]({});>;);out;']
        self.__load_osm_data(tag="highway", tag_value="traffic_signals", queries=queries)

    def __cache_name(self, bbox_str: str, element: str, tag_text: str):
        m = hashlib.md5()
        m.update(bbox_str.encode())
        m.update(element.encode())
        m.update(tag_text.encode())
        return m.hexdigest()

    def __get_boundaries(self):
        from shapely.geometry import Polygon, box
        from pyproj import Transformer

        self.__model_boundaries = Polygon(box(*self.__geotool.model_area.bounds))
        self.__reverse_transformer = Transformer.from_crs(self.srid, 4326, always_xy=True)
        self.__transformer = Transformer.from_crs(4326, self.srid, always_xy=True)

        return self.__model_boundaries
