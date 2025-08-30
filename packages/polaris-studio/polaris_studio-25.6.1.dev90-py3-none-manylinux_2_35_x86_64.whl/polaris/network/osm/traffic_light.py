# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import Optional

import numpy as np
from shapely.geometry import Point


class TrafficLight:
    """Basic class to represent a traffic light from OSM"""

    def __init__(self):
        self.osm_id = -1
        self.geo: Optional[Point] = None
        self.distance = np.inf
