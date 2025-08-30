# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from pathlib import Path
from typing import Optional, Dict

import numpy as np
import openmatrix as omx
import pandas as pd
from polaris.skims.highway.export_hwy_omx import export_hwy_omx
from polaris.skims.utils.basic_skim import SkimBase


class HighwaySkim(SkimBase):
    """Polaris Skims class

    ::

        from polaris.skims.highway.highway_skim import HighwaySkim

        skims = HighwaySkim()

        # Load skims for highway
        skims.open('path/to/hwy/skims')

        # accessing skims is easy
        m1 = skims.time[1440] # time for the interval
        m2 = skims.distance[720] # distance for the interval 720
        m3 = skims.cost[240] # cost for the interval 240

        # We can also access skims like we do for PT
        time_morning = skims.get_skims(interval=240, metric="time")

    """

    prefix = "highway"

    def __init__(self, filename: Optional[PathLike] = None):
        SkimBase.__init__(self)
        self._infinite = 1.7895698e07
        self.time: Dict[int, np.ndarray] = {}
        self.distance: Dict[int, np.ndarray] = {}
        self.cost: Dict[int, np.ndarray] = {}
        self.metrics = ["cost", "distance", "time"]
        if filename:
            self.open(filename)

    def open(self, path_to_file: PathLike):
        """Loads the highway skim data

        Args:
            *path_to_file* (:obj:`str`): Full file path to the highway skim
        """
        if str(Path(path_to_file).suffix).lower() != ".omx":
            url = "https://git-out.gss.anl.gov/polaris/code/polaristools"
            raise ValueError(f"bin format is no longer supported. For conversion to OMX check  {url}")

        infile = omx.open_file(path_to_file)
        self.index = pd.DataFrame(infile.mapping("taz").items(), columns=["zones", "index"])
        intervals = set()
        for m in infile.list_matrices():
            matrix = infile[m]
            if any(attr not in matrix.attrs for attr in ["metric", "timeperiod"]):
                continue

            intr = int(matrix.attrs["timeperiod"].astype(str))
            metr = matrix.attrs["metric"].astype(str)
            intervals.add(intr)

            data = np.array(matrix)
            data[data >= self._infinite] = np.inf
            if metr == "time":
                self.time[intr] = np.array(data)
            elif metr == "distance":
                self.distance[intr] = np.array(data)
            elif metr == "cost":
                self.cost[intr] = np.array(data)
        self.intervals = sorted(intervals)
        infile.close()

    def create_empty(self, intervals: list, zones: int):
        """Creates a new skim data cube for a given set of intervals and number of zones.
           All matrices are filled with zeros

        Args:
            *intervals* (:obj:`list`): List of all intervals this skim file should have
            *zones* (:obj:`int`): Number of zones for this skim
        """

        self.index = pd.DataFrame({"zones": 1 + np.arange(zones), "index": np.arange(zones)})
        self.intervals = sorted(intervals)

        for interv in self.intervals:
            for dct in [self.time, self.cost, self.distance]:
                dct[interv] = np.zeros((zones, zones), dtype="f")

    def get_skims(self, interval=None, metric=None, **kwargs):
        """Gets skim data for specified mode/interval/metric.  These filters are not, however, required.
        If one or more parameters it not provided, a dictionary (or nested dictionaries) will be returned

        Args:
            *interval* `Optional` (:obj:`int`): The time interval of interest
            *metric* `Optional` (:obj:`str`): Metric
        """

        data = {metr: {interv: self.__dict__[metr][interv] for interv in self.intervals} for metr in self.metrics}

        if interval:
            data = {mt: data[mt][interval] for mt in self.metrics}
        if metric:
            data = data[metric.lower()]

        return data

    def remove_interval(self, interval: int):
        """Removes one interval from this skim. Operation happens in memory only. It does NOT alter skim on disk

            Args:
        *interval* (:obj:`int`): Interval to remove from the skim
        """
        if interval not in self.intervals:
            raise ValueError(f"Interval {interval} does not exist")

        for dct in [self.time, self.cost, self.distance]:
            del dct[interval]
        self.intervals.remove(interval)

    def add_interval(self, interval: int, copy_interval=None):
        """Adds a new interval to the skim matrix

        Args:
            *interval* (:obj:`int`): Interval to be added to the skim data cube
            *copy_interval* `Optional` (:obj:`int`): Interval to be copied into the new interval. Arrays of zeros
            are added if not provided
        """
        copy_from = copy_interval or self.intervals[0]
        if copy_from not in self.intervals:
            raise ValueError(f"Interval {copy_from} does not exist")

        if interval in self.intervals:
            raise ValueError(f"Interval {interval} already exists int the skim data cube")

        for dct in [self.time, self.cost, self.distance]:
            dct[interval] = np.zeros_like(dct[copy_from]) if copy_interval is None else np.array(dct[copy_interval])

        self.intervals = sorted(self.intervals + [interval])

    def write_to_file(self, path_to_file: PathLike):
        if Path(path_to_file).exists():
            raise FileExistsError("Cannot overwrite OMX file")
        export_hwy_omx(self.get_skims(), path_to_file, self.index, self.intervals)
