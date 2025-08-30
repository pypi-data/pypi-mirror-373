# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import importlib.util as iutil
from typing import Union, List

from shapely.geometry import Point, Polygon, LineString, MultiPoint, MultiPolygon, MultiLineString
from shapely.wkb import loads

if iutil.find_spec("qgis") is not None:
    from qgis.core import QgsSpatialIndex as Index  # type: ignore
    from qgis.core import QgsGeometry, QgsFeature

    env = "QGIS"
else:
    from rtree.index import Index as Index  # type: ignore

    env = "Python"


class GeoIndex:
    """Implements a generic GeoIndex class that uses the QGIS index when using the GUI and RTree otherwise"""

    def __init__(self):
        self.idx = Index()
        self.built = False

    def build_from_layer(self, layer) -> dict:
        self.built = True
        self.idx = Index(layer.getFeatures())
        return {f.id(): loads(f.geometry().asWkb().data()) for f in layer.getFeatures()}

    def insert(
        self, feature_id: int, geometry: Union[Point, Polygon, LineString, MultiPoint, MultiPolygon, MultiLineString]
    ) -> None:
        """Inserts a valid shapely geometry in the index

        Args:
            *feature_id* (:obj:`int`): ID of the geometry being inserted
            *geo* (:obj:`Shapely geometry`): Any valid shapely geometry
        """
        self.built = True
        if env == "QGIS":
            g = QgsGeometry()
            g.fromWkb(geometry.wkb)
            feature = QgsFeature()
            feature.setGeometry(g)
            feature.setId(feature_id)
            self.idx.addFeature(feature)
        else:
            self.idx.insert(feature_id, geometry.bounds)

    def nearest(self, geo: Union[Point, Polygon, LineString, MultiPoint, MultiPolygon], num_results) -> List[int]:
        """Finds nearest neighbor for a given geometry

        Args:
            *geo* (:obj:`Shapely geometry`): Any valid shapely geometry
            *num_results* (:obj:`int`): A positive integer for the number of neighbors to return
        Return:
            *neighbors* (:obj:`List[int]`): List of IDs of the closest neighbors in the index
        """
        if env == "QGIS":
            g = QgsGeometry()
            g.fromWkb(geo.wkb)
            return self.idx.nearestNeighbor(g, num_results)
        else:
            return self.idx.nearest(geo.bounds, num_results)

    def delete(self, feature_id, geometry: Union[Point, Polygon, LineString, MultiPoint, MultiPolygon]):
        self.idx.delete(feature_id, geometry.bounds)

    def reset(self):
        self.idx = Index()
        self.built = False
