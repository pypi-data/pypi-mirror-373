# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import csv
from pathlib import Path

import numpy as np
import yaml
from polaris.utils.database.db_utils import commit_and_close, read_and_close
from tables import open_file


class PricingSetter:
    BATCH_SIZE = 2000000

    def __init__(self, pricing_configuration_file, supply_db=None, demand_db=None, result_db=None):
        self.supply_db = supply_db
        self.demand_db = demand_db
        self.result_db = result_db
        self.pricing_type = None
        self.links = None
        self.target_revenue = None

        # CP Defaults
        self.baseline_price_per_mile = 0
        self.cost_per_avg_delay_sec = 0.005
        self.previous_weight = 0.6
        self.previous_step_weight = 0.2
        self.this_step_weight = 0.2

        # Cordon Defaults
        self.cordon_charge_dollar_per_entry = 5.0
        self.links_to_charge_cordon_toll_file = Path("cordon_links.csv")

        self.pricing_configuration_file = Path(pricing_configuration_file)

        self.initialize_pricing()

        self.revenue_sql = """
            SELECT person_toll + tnc_toll as total_toll
            FROM
                (
                    SELECT sum(toll) as person_toll
                    FROM Trip
                    WHERE type = 22 or ((mode == 0 or mode == 9) and type == 11)
                ) as t1,
                (
                    SELECT sum(toll) as tnc_toll
                    FROM TNC_Trip
                ) as t2;
        """
        self.estimated_revenue_sql = "SELECT sum(link_out_volume) FROM LinkMOE WHERE link_uid in (SELECT link*2 + dir as link_uid FROM a.Toll_Pricing);"
        self.get_toll_links_in_db = "SELECT link*2 + dir as link_uid FROM Toll_Pricing"

    def initialize_pricing(self):
        if not self.pricing_configuration_file.exists():
            raise FileExistsError(f"No such file: {self.pricing_configuration_file}")

        with open(self.pricing_configuration_file) as file:
            pricing_settings = yaml.load(file, Loader=yaml.FullLoader)

        self.pricing_type = pricing_settings.get("PricingType", "cordon")

        if self.pricing_type == "CP":
            self.baseline_price_per_mile = pricing_settings.get("baseline_price_per_mile", self.baseline_price_per_mile)
            self.cost_per_avg_delay_sec = pricing_settings.get("cost_per_avg_delay_sec", self.cost_per_avg_delay_sec)
            self.links = self.get_links()
        elif self.pricing_type == "cordon":
            self.cordon_charge_dollar_per_entry = pricing_settings.get(
                "cordon_charge_dollar_per_entry", self.cordon_charge_dollar_per_entry
            )
            self.links_to_charge_cordon_toll_file = Path(
                pricing_settings.get("links_to_charge_cordon_toll_file", self.links_to_charge_cordon_toll_file)
            )

    def get_links(self):
        with read_and_close(self.supply_db) as conn:
            links_dir = {}
            for link, lanes_ab, lanes_ba, length in conn.execute("SELECT link, lanes_ab, lanes_ba, length from link"):
                if lanes_ab > 0:
                    l = {"link": link, "uid": link * 2, "lanes": lanes_ab, "length": length}
                    links_dir[l["link"], 0] = l
                if lanes_ba > 0:
                    l = {"link": link, "uid": link * 2 + 1, "lanes": lanes_ba, "length": length}
                    links_dir[l["link"], 1] = l

        return links_dir

    def set_price_no_result(self):
        tuples = []

        for key, link in self.links.items():
            link_id, dir = key
            tuples.append(str((link_id, dir, 0, 86400, self.baseline_price_per_mile * link["length"] / 1609.0)))

        with commit_and_close(self.supply_db) as conn:
            conn.execute("delete from toll_pricing")
            query = "INSERT into Toll_pricing (link, dir, start_time, end_time, price) VALUES " + ",".join(tuples)
            conn.execute(query)

    def set_prices_with_result(self):
        with open_file(self.result_db, mode="r") as h5file:
            num_timesteps = h5file.root.link_moe._v_attrs.num_timesteps
            timestep = h5file.root.link_moe._v_attrs.timestep
            link_uids = np.array(h5file.root.link_moe.link_uids).flatten()
            link_travel_delays = np.array(h5file.root.link_moe.link_travel_delay).flatten()

        if self.target_revenue:
            with read_and_close(self.demand_db) as conn:
                revenue = conn.execute("SELECT SUM(toll) from trip").fetchone()[0]
            multiplier = self.target_revenue / revenue
        else:
            multiplier = 1.0

        prices_per_uid = {}
        for u, link_uid in enumerate(link_uids[0, :]):
            prices_per_uid[link_uid] = []

            for step in range(num_timesteps):
                record = {
                    "start_time": step * timestep,
                    "end_time": (step + 1) * timestep,
                    "delay": link_travel_delays[step, u],
                    "previous_price": -1,
                }
                prices_per_uid[link_uid].append(record)

        prevailing_prices = self.get_prevailing_prices()

        if len(prevailing_prices) == len(prices_per_uid):
            print("records look consistent...")

        tuples_out = []

        for link_uid in prices_per_uid:
            last_price = None

            link = int(link_uid / 2)
            dire = link_uid % 2

            if link_uid not in prevailing_prices:
                continue

            for record in prices_per_uid[link_uid]:
                prev_price = None

                unfiltered_price = (
                    self.baseline_price_per_mile * self.links[link, dire]["length"] / 1609.0
                    + record["delay"] * self.cost_per_avg_delay_sec
                )

                for record_prevailing in prevailing_prices[link_uid]:
                    if (
                        record_prevailing["start_time"] >= record["start_time"]
                        and record_prevailing["end_time"] >= record["end_time"]
                    ):
                        prev_price = record_prevailing["price"]
                        break

                if prev_price and last_price:
                    price = (
                        self.previous_weight * prev_price
                        + self.previous_step_weight * last_price
                        + self.this_step_weight * unfiltered_price
                    )

                elif last_price:
                    last_price_weight = self.previous_step_weight + self.previous_weight / 2.0
                    this_step_weight = self.this_step_weight + self.previous_weight / 2.0
                    price = last_price_weight * last_price + this_step_weight * unfiltered_price

                elif prev_price:
                    previous_price_weight = self.previous_weight + self.previous_step_weight / 2.0
                    this_step_weight = self.this_step_weight + self.previous_step_weight / 2.0
                    price = previous_price_weight * prev_price + this_step_weight * unfiltered_price
                else:
                    price = unfiltered_price

                last_price = price

                tuples_out.append(str((link, dire, record["start_time"], record["end_time"], multiplier * price)))

        with commit_and_close(self.supply_db) as conn:
            conn.execute("delete from toll_pricing")

            num_batches = int(len(tuples_out) / self.BATCH_SIZE) + 1
            for i in range(int(num_batches)):
                tps = tuples_out[i * self.BATCH_SIZE : (i + 1) * self.BATCH_SIZE]
                if tps:
                    query = "INSERT into Toll_pricing (link, dir, start_time, end_time, price) VALUES " + ",".join(tps)
                    print(len(tps))
                    conn.execute(query)

    def get_prevailing_prices(self):
        with read_and_close(self.supply_db) as conn:
            query = "SELECT link, dir, start_time, end_time, price from Toll_Pricing"
            rows = conn.execute(query).fetchall()

        prices_per_uid = {}
        for link, dir, start_time, end_time, price in rows:
            uid = 2 * link + dir
            if uid not in prices_per_uid:
                prices_per_uid[uid] = []

            prices_per_uid[uid].append({"start_time": start_time, "end_time": end_time, "delay": -1, "price": price})
        conn.close()
        return prices_per_uid

    def get_total_revenue(self):
        with read_and_close(self.demand_db) as conn:
            return conn.execute(self.revenue_sql).fetchone()[0]

    def get_total_estimated_revenue(self):
        with read_and_close(self.supply_db) as conn:
            tolled_link_uids = conn.execute(self.get_toll_links_in_db).fetchall()

        with open_file(self.result_db, mode="r") as h5file:
            link_uids = np.array(h5file.root.link_moe.link_uids).flatten()
            link_out_volume = np.array(h5file.root.link_moe.link_out_volume).flatten()

        total_demand = 0.0

        for link_uid in tolled_link_uids:
            idx = np.where(link_uids == link_uid)
            total_demand += sum(link_out_volume[:, idx[1]])

        # revenue_generated = conn.execute(self.estimated_revenue_sql).fetchone()[0] * self.cordon_charge_dollar_per_entry
        return total_demand * self.cordon_charge_dollar_per_entry

    def set_cordon_links_in_supply(self):
        if self.pricing_type != "cordon":
            raise Exception("Do not set cordon links when pricing type is: ", self.pricing_type)

        tuples = []

        with open(self.links_to_charge_cordon_toll_file) as link_file:
            csv_reader = csv.DictReader(link_file)
            for row in csv_reader:
                link_id, dir = row["link"], row["dir"]
                tuples.append(str((link_id, dir, 0, 86400, self.cordon_charge_dollar_per_entry)))

        with commit_and_close(self.supply_db) as conn:
            conn.execute("delete from toll_pricing")
            query = "INSERT into Toll_pricing (link, dir, start_time, end_time, price) VALUES " + ",".join(tuples)
            conn.execute(query)
