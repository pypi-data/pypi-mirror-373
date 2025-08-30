# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from typing import List

import numpy as np
import pandas as pd

from polaris.utils.database.db_utils import has_column, read_and_close
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.signals import SIGNAL


class GlobalChecker:
    """Model Checker"""

    checking = SIGNAL(object)

    def __init__(self, model):
        from polaris.runs.convergence.config.convergence_config import ConvergenceConfig

        self.config: ConvergenceConfig = model.run_config
        self._fldr_path = self.config.data_dir
        self._supply_file = model.supply_file
        self._demand_file = model.demand_file
        self._freight_file = model.freight_file
        polaris_logging()

        self.checks_completed = 0
        self.errors: List[str] = []

    def critical(self):
        """Runs set of tests for issues known to crash Polaris"""

        self._trips_valid_locations()
        self._sf1_locations()
        self._fundamental_diagram()

        if self._freight_file.exists():
            self._airports_valid_locations()
            self._railports_valid_locations()
            self._international_ports_valid_locations()
            self._truck_poe_valid_locations()
            self._check_counties_populated()

        return self.errors

    def _trips_valid_locations(self):
        sql = """SELECT DISTINCT(location) FROM (SELECT DISTINCT(origin) location FROM Trip
                                                  UNION ALL
                                                 SELECT DISTINCT(destination) location FROM Trip )"""

        with read_and_close(self._demand_file) as conn:
            trip_locations = pd.read_sql(sql, conn)
            if trip_locations.empty:
                return
        with read_and_close(self._supply_file) as conn:
            supply_locations = pd.read_sql("SELECT location from Location", conn)

        if trip_locations[~trip_locations.location.isin(supply_locations.location)].empty:
            return

        self.errors.append("Trips refer to locations that do not exist in the supply file")

    def _sf1_locations(self):
        with read_and_close(self._supply_file) as conn:
            location_census_col = "popsyn_region" if has_column(conn, "Location", "popsyn_region") else "census_zone"
            sql = f"""
                 SELECT DISTINCT({location_census_col})
                 FROM Location
                 WHERE land_use IN ('RES', 'MIX', 'ALL', 'RESIDENTIAL-SINGLE', 'RESIDENTIAL-MULTI')
            """
            zones_with_locations = pd.read_sql(sql, conn)[location_census_col].astype(np.int64).to_numpy()

        for sf1_name in ["sf1.csv", "sf1.txt"]:
            sf1_file = self._fldr_path / sf1_name
            if sf1_file.exists():
                break

        if not sf1_file.exists():
            return
        sep = "," if sf1_name.endswith(".csv") else "\t"
        sf1 = pd.read_csv(sf1_file, sep=sep)
        col = sf1.columns[0]
        missing = sf1[~sf1[col].astype(np.int64).isin(zones_with_locations)]
        if missing.empty:
            return
        logging.warning("There are census tracts with population that have no corresponding residential location")
        self.errors.append("There are census tracts with population that have no corresponding residential location")
        self.errors.append(missing[col].to_list())

    def _load_links_with_shockwave_speed(self, network_config=None):

        link_sql = """SELECT link, 0 as dir, length, type, fspd_ab speed, lanes_ab lanes, cap_ab cap_from_db FROM Link l
                      INNER JOIN link_type lt on l.type=lt.link_type
                             WHERE l.lanes_ab>0 AND (lt.use_codes like '%AUTO%' OR lt.use_codes like '%TRUCK%' OR
                             lt.use_codes like '%HOV%' OR lt.use_codes like '%TAXI%')
                      UNION ALL
                      SELECT link, 1 as dir, length, type, fspd_ba speed, lanes_ba lanes, cap_ba cap_from_db FROM Link l
                      INNER JOIN link_type lt on l.type=lt.link_type
                             WHERE l.lanes_ba>0 AND (lt.use_codes like '%AUTO%' OR lt.use_codes like '%TRUCK%' OR
                             lt.use_codes like '%HOV%' OR lt.use_codes like '%TAXI%')"""

        with read_and_close(self._supply_file) as conn:
            links = pd.read_sql(link_sql, conn)

        def shockwave_speed(jam_density, speeds, capacities):
            critical_density = capacities / speeds
            return capacities / (jam_density - critical_density)

        def shockwave_speed_pw_linear(jam_density, speeds, capacities, beta):
            critical_density = beta * capacities / speeds
            return capacities / (jam_density - critical_density)

        network_config = network_config or self.config.load_scenario_json()["Network simulation controls"]
        capacity_local = self.config.capacity_local or network_config.get("capacity_local", 1400)
        capacity_arterial = self.config.capacity_arterial or network_config.get("capacity_arterial", 1600)
        capacity_expressway = self.config.capacity_expressway or network_config.get("capacity_expressway", 1900)

        freeway_types = ["FREEWAY", "EXPRESSWAY", "EXTERNAL"]
        arterial_types = ["PRINCIPAL", "MAJOR", "MINOR", "OTHER"]
        ramp_types = ["RAMP", "ON_RAMP", "OFF_RAMP"]
        is_ramp = links["type"].isin(ramp_types)

        def idx(lower, upper):
            spd = links["speed"] / 1609 * 3600
            return is_ramp & (spd > lower) & (spd <= upper)

        links = links.assign(capacity=capacity_local)
        links.loc[links["type"].isin(freeway_types), "capacity"] = capacity_expressway
        links.loc[links["type"].isin(arterial_types), "capacity"] = capacity_arterial
        links.loc[is_ramp, "capacity"] = capacity_arterial
        links.loc[idx(50, 99999), "capacity"] = capacity_expressway
        links.loc[idx(40, 50), "capacity"] = capacity_expressway - 100
        links.loc[idx(30, 40), "capacity"] = capacity_expressway - 200
        links.loc[idx(20, 30), "capacity"] = capacity_expressway - 300

        links["cap_from_db"] /= links["lanes"]
        links["capacity"] = links[["capacity", "cap_from_db"]].max(axis=1) / 3600.0

        if hasattr(self.config, "jam_density"):
            jam_density = self.config.jam_density
        else:
            logging.critical("Jam density not set in the configuration. Using default value of 220 veh/mile")
            jam_density = 220
        jam_density /= 1609.0

        if network_config.get("piecewise_linear_fd", False):
            beta = network_config["beta_piecewise_linear_fd"]
            return links.assign(
                shockwave_speed=shockwave_speed_pw_linear(jam_density, links.speed, links.capacity, beta)
            )
        else:
            return links.assign(shockwave_speed=shockwave_speed(jam_density, links.speed, links.capacity))

    def _fundamental_diagram(self):
        links = self._load_links_with_shockwave_speed()
        errors = links[links.shockwave_speed < 0]
        if errors.empty:
            return
        self.errors.append("Fundamental diagram violated. There are links with negative shockwave speeds")
        self.errors.append(list(zip(errors.link, errors.shockwave_speed)))

    @staticmethod
    def check_location_fk(supply_db_file, ref_db_file, table_name):
        with read_and_close(ref_db_file) as conn:
            locations = pd.read_sql(f"SELECT DISTINCT(location) FROM {table_name}", conn)
            if locations.empty:
                return []
        with read_and_close(supply_db_file) as conn:
            supply_locations = pd.read_sql("SELECT location from Location", conn)

        if locations[~locations.location.isin(supply_locations.location)].empty:
            return []

        return [f"Table {table_name} refers to locations that do not exist in the supply database"]

    def _airports_valid_locations(self):
        self.errors.extend(GlobalChecker.check_location_fk(self._supply_file, self._freight_file, "Airport_Locations"))

    def _railports_valid_locations(self):
        self.errors.extend(GlobalChecker.check_location_fk(self._supply_file, self._freight_file, "Railport_Locations"))

    def _international_ports_valid_locations(self):
        self.errors.extend(
            GlobalChecker.check_location_fk(self._supply_file, self._freight_file, "International_Port_Locations")
        )

    def _truck_poe_valid_locations(self):
        self.errors.extend(GlobalChecker.check_location_fk(self._supply_file, self._freight_file, "Truck_Poe"))

    def _check_counties_populated(self):
        with read_and_close(self._supply_file) as conn:
            counties_loc = pd.read_sql("SELECT DISTINCT(county) FROM Location", conn)
            counties_gis = pd.read_sql("SELECT DISTINCT(county) FROM Counties", conn)

        if counties_loc.empty:
            self.errors.append("There is no county information attached to Locations")
        if counties_gis.empty:
            self.errors.append("The Counties table is not populated, it is required for freight analysis")
