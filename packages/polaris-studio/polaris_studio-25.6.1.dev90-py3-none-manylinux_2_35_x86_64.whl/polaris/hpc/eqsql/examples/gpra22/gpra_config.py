# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import re
from dataclasses import dataclass
from pathlib import Path

# Austin	            00000000
# Chicago	            01000000
# Detroit	            10000000
# Atlanta	            11000000
cities_by_id = {0: "Austin", 1: "Chicago", 2: "Detroit", 3: "Atlanta", 4: "Grid"}
cities_to_id = {"Austin": 0, "Chicago": 1, "Detroit": 2, "Atlanta": 3, "Grid": 4}

city_mask = 0b11000000
transit_mask = 0b00100000
fmlm_mask = 0b00010000
signal_coord_mask = 0b00001000
pricing_mask = 0b00000100
tele_commute_and_ecomm_mask = 0b00000010
veh_tech_mask = 0b00000001


@dataclass
class GPRAConfig(object):
    city: str
    transit: bool = False
    fmlm: bool = False
    signal_coord: bool = False
    pricing: bool = False
    tele_commute_and_ecomm: bool = False
    veh_tech: bool = False
    payload = None
    task_container = None

    @staticmethod
    def from_run_id(run_id):
        run_id = int(run_id)
        # TODO: JC 2022-09-23 - Revert range to 0,256 after Grid testing is finished
        if run_id < 0 or run_id > 320:
            raise f"Not a valid GPRA run id: {run_id}"

        city = cities_by_id[(run_id >> 6)]
        transit = bool(run_id & transit_mask)
        fmlm = bool(run_id & fmlm_mask)
        signal_coord = bool(run_id & signal_coord_mask)
        pricing = bool(run_id & pricing_mask)
        tele_commute_and_ecomm = bool(run_id & tele_commute_and_ecomm_mask)
        veh_tech = bool(run_id & veh_tech_mask)
        return GPRAConfig(city, transit, fmlm, signal_coord, pricing, tele_commute_and_ecomm, veh_tech)

    @staticmethod
    def is_valid_run_id(run_id):
        try:
            run_id = int(run_id)
            return run_id >= 0 and run_id <= 320
        except:
            return False

    def to_run_id(self):
        """
        > twin_config = gpra_config
        > twin_config.transit = False
        > twin_run_id = twin_config.to_run_id()
        """
        run_id = (
            (cities_to_id[self.city] << 6)
            | int(self.transit) * transit_mask
            | int(self.fmlm) * fmlm_mask
            | int(self.signal_coord) * signal_coord_mask
            | int(self.pricing) * pricing_mask
            | int(self.tele_commute_and_ecomm) * tele_commute_and_ecomm_mask
            | int(self.veh_tech) * veh_tech_mask
        )
        return f"{run_id:>03}"

    @staticmethod
    def to_run_id_static(run_id):
        if isinstance(run_id, str):
            return run_id
        if isinstance(run_id, int):
            return f"{run_id:>03}"
        if isinstance(run_id, Path):
            run_id = re.match(".*([0-9][0-9][0-9])_.*", str(run_id))[1]
            return run_id

    @staticmethod
    def to_run_ids(run_ids):
        if isinstance(run_ids, str) or isinstance(run_ids, int):
            return [GPRAConfig.to_run_id_static(run_ids)]
        return [GPRAConfig.to_run_id_static(e) for e in run_ids]

    def to_excel(self):
        """String based repr that can be used to populate the excel sheet and double check the logic of the above."""
        bools = [
            "True" if e else "False"
            for e in [
                self.transit,
                self.fmlm,
                self.signal_coord,
                self.pricing,
                self.tele_commute_and_ecomm,
                self.veh_tech,
            ]
        ]
        return " ".join([self.to_run_id(), self.city] + bools)

    def is_base(self):
        return not any(
            [self.transit, self.fmlm, self.signal_coord, self.pricing, self.tele_commute_and_ecomm, self.veh_tech]
        )

    def db_name(self):
        return "Campo" if self.city == "Austin" else self.city
