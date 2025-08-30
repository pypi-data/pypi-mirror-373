# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike


class Skims:
    def __init__(self, highway_path: PathLike, transit_path: PathLike):
        self.highway_path = highway_path
        self.transit_path = transit_path

    @property
    def highway(self):
        from polaris.skims.highway.highway_skim import HighwaySkim

        return HighwaySkim.from_file(self.highway_path)

    @property
    def transit(self):
        from polaris.skims.transit.transit_skim import TransitSkim

        return TransitSkim.from_file(self.transit_path)
