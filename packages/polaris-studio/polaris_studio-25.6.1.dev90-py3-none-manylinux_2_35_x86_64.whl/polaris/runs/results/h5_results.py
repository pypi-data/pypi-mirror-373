# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import numpy as np
import pandas as pd
from tables import open_file

from polaris.runs.results.link_volumes import aggregate_link_volumes, pivot_to_AB_direction
from polaris.runs.results.result_version import get_version_from_handle


class H5_Results(object):
    def __init__(self, filename):
        self.filename = filename
        with open_file(self.filename, mode="r") as h5file:
            self.capabilities = get_version_from_handle(h5file)
            self.num_timesteps = h5file.root.link_moe._v_attrs.num_timesteps if self.capabilities["link_moe"] else None

        if self.capabilities["link_moe"]:
            self.cache_timesteps()
            self.num_links = self.get_vector("link_moe", "link_uids").shape[0]
            self.num_turns = self.get_vector("turn_moe", "turn_uids").shape[0]
        self.path_lu = None
        self.path_mm_lu = None

    def get_link_volumes(self, population_scale_factor=1.0, periods=None):
        uids = self.get_vector("link_moe", "link_uids")
        scale_factor = 1.0 / population_scale_factor
        in_vols = self.get_array("link_moe", "link_in_volume") * scale_factor
        df = pd.DataFrame(in_vols, columns=uids)
        return pivot_to_AB_direction(aggregate_link_volumes(df, periods))

    def cache_path_lu(self):
        if self.path_lu is None:
            self.path_lu = self.extract_index_lu(self.get_paths())

    def cache_path_mm_lu(self):
        if self.path_mm_lu is None:
            self.path_mm_lu = self.extract_index_lu(self.get_mm_paths())

    def get_vector(self, group, value):
        with open_file(self.filename, mode="r") as h5file:
            return np.array(h5file.root._f_get_child(group)._f_get_child(value)).flatten()

    def list_tables(self):
        with open_file(self.filename, mode="r") as h5file:
            return [node._v_pathname.replace("/", "") for node in h5file.walk_nodes(classname="Table")]

    def list_groups(self):
        with open_file(self.filename, mode="r") as h5file:
            return [node._v_pathname.replace("/", "") for node in h5file.walk_nodes(classname="Group")]

    def get_array(self, group, table):
        with open_file(self.filename, mode="r") as h5file:
            if group not in h5file.root or table not in h5file.root._f_get_child(group):
                return None
            return np.array(h5file.root._f_get_child(group)._f_get_child(table))

    mm_cols = [
        "gen_cost",
        "duration",
        "arrival_time",
        "bus_wait_time",
        "rail_wait_time",
        "comm_rail_wait_time",
        "walk_time",
        "bike_time",
        "bus_ivtt",
        "rail_ivtt",
        "comm_rail_ivtt",
        "car_time",
        "wait_count",
        "transfer_pen",
        "standing_pen",
        "capacity_pen",
        "monetary_cost",
        "tnc_wait_count",
        "tnc_wait_time",
    ]
    path_mm_cols = (
        ["path_id", "mode", "num_switches", "link_first_index", "link_last_index"]
        + [f"est_{e}" for e in mm_cols]
        + [f"actual_{e}" for e in mm_cols]
    )
    path_mm_link_cols = [
        "path_id",
        "link_uuid",
        "entering_time",
        "transit_vehicle_trip_id",
        "stop_seq_nr",
        "est_travel_time",
        "act_travel_time",
        "est_arrival_time",
        "act_arrival_time",
        "est_gen_cost",
        "act_gen_cost",
        "est_wait_count",
        "act_wait_count",
        "est_tnc_wait_count",
        "est_wait_time",
        "act_wait_time",
        "est_transfer_penalty",
        "act_transfer_penalty",
        "est_standing_penalty",
        "act_standing_penalty",
        "est_capacity_penalty",
        "act_capacity_penalty",
        "est_monetary_cost",
        "act_monetary_cost",
    ]
    path_cols = ["path_id", "link_first_index", "link_last_index", "unit_first_index", "unit_last_index"]
    path_link_cols = ["path_id", "link_uuid", "entering_time", "travel_time"]
    path_link_cols += ["energy_consumption", "routed_travel_time"]
    timesteps = None  # [14400, 28800, 43200, 57600, 72000, 86399]

    def get_paths(self):
        self.cache_timesteps()

        def load_timestep(t):
            df = pd.DataFrame(self.get_array("paths", f"path_timestep_{t}"), columns=self.path_cols)
            return df.assign(timestep=t)

        return self.integerize_cols(pd.concat([load_timestep(i) for i in self.timesteps]))

    def cache_timesteps(self):
        if self.timesteps is not None:
            return
        with open_file(self.filename, mode="r") as f:
            self.timesteps = [
                e._v_pathname.split("_")[-1] for e in f.list_nodes("/paths") if "path_timestep_" in e._v_pathname
            ]

    def integerize_cols(self, df):
        for c in ["path_id", "timestep", "link_first_index", "link_last_index"]:
            df[c] = df[c].astype(int)
        return df

    def extract_index_lu(self, df):
        return pd.Series(list(zip(df.timestep, df.link_first_index, df.link_last_index)), index=df.path_id).to_dict()

    def get_mm_paths(self):
        self.cache_timesteps()
        cols = [e for e in self.path_mm_cols if any(f"{p}" in e for p in ["_time", "_pen", "cost", "ivtt", "duration"])]

        def load_timestep(t):
            df = pd.DataFrame(self.get_array("paths", f"path_mm_timestep_{t}"), columns=self.path_mm_cols)
            df[cols] /= 1000.0
            return df.assign(timestep=t)

        return pd.concat([load_timestep(i) for i in self.timesteps]).sort_values("path_id")

    def get_path_links(self, path_id=None):
        self.cache_timesteps()
        if path_id is not None:
            self.cache_path_lu()
            timestep, first_idx, last_idx = self.path_lu.get(path_id)
            links = self.get_path_links_for_timestep(timestep)
            return links.iloc[first_idx : last_idx + 1]

        return pd.concat([self.get_path_links_for_timestep(t) for t in self.timesteps])

    def get_path_links_for_timestep(self, timestep):
        links = pd.DataFrame(
            data=self.get_array("paths", f"path_links_timestep_{timestep}"), columns=self.path_link_cols
        )
        links["link_id"] = np.floor(links.link_uuid.to_numpy() / 2).astype(int)
        links["link_dir"] = (links.link_uuid.to_numpy() % 2).astype(int)
        cols = ["entering_time", "travel_time", "routed_travel_time"]
        links[cols] /= 1000.0
        return links

    def get_path_mm_links_for_timestep(self, timestep):
        links = pd.DataFrame(
            data=self.get_array("paths", f"path_mm_links_timestep_{timestep}"), columns=self.path_mm_link_cols
        )
        links["link_id"] = np.floor(links.link_uuid.to_numpy() / 2).astype(int)
        links["link_dir"] = (links.link_uuid.to_numpy() % 2).astype(int)

        cols = ["entering_time", "est_travel_time", "act_travel_time", "est_arrival_time", "act_arrival_time"]
        cols += ["est_gen_cost", "act_gen_cost", "est_wait_time", "act_wait_time"]
        cols += ["est_transfer_penalty", "act_transfer_penalty", "est_standing_penalty", "act_standing_penalty"]
        cols += ["est_capacity_penalty", "act_capacity_penalty", "est_monetary_cost", "act_monetary_cost"]
        links[cols] /= 1000.0

        return links

    def get_path_mm_links(self, path_id=None):
        self.cache_timesteps()
        if path_id is not None:
            self.cache_path_mm_lu()
            timestep, first_idx, last_idx = self.path_mm_lu.get(path_id)
            links = self.get_path_mm_links_for_timestep(timestep)
            return links.iloc[first_idx : last_idx + 1]
        return pd.concat([self.get_path_mm_links_for_timestep(t) for t in self.timesteps])

    def get_array_v0(self, f, group, table):
        tables = {
            "link_moe": [
                "link_travel_time",
                "link_travel_time_standard_deviation",
                "link_queue_length",
                "link_travel_delay",
                "link_travel_delay_standard_deviation",
                "link_speed",
                "link_density",
                "link_in_flow_rate",
                "link_out_flow_rate",
                "link_in_volume",
                "link_out_volume",
                "link_speed_ratio",
                "link_in_flow_ratio",
                "link_out_flow_ratio",
                "link_density_ratio",
                "link_travel_time_ratio",
                "num_vehicles_in_link",
                "volume_cum_MDT",
                "volume_cum_HDT",
                "entry_queue_length",
            ],
            "turn_moe": [
                "turn_penalty",
                "turn_penalty_sd",
                "inbound_turn_travel_time",
                "outbound_turn_travel_time",
                "turn_flow_rate",
                "turn_flow_rate_cv",
                "turn_penalty_cv",
                "total_delay_interval",
                "total_delay_interval_cv",
            ],
        }
        return f[group][:, :, tables[group].index(table)].T

    def get_vmt_vht(self, population_scale_factor):

        if not self.capabilities["link_moe"]:
            raise RuntimeError("This result file does not contain link MOE data")

        scale_factor = 1.0 / population_scale_factor
        lengths = self.get_vector("link_moe", "link_lengths") / 1609.3
        counts = self.get_array("link_moe", "link_out_volume") * scale_factor
        travel_times = self.get_array("link_moe", "link_travel_time") / 3600.0
        uuids = pd.Series(self.get_vector("link_moe", "link_uids"), name="linknr")

        # Construct an aggregation matrix (num_timesteps x num_hours)
        new_num_steps = 24
        aggregation_vector = np.zeros((self.num_timesteps, new_num_steps))
        ratio = int(self.num_timesteps / new_num_steps)
        for u in range(new_num_steps):
            aggregation_vector[u * ratio : (u + 1) * ratio, u] = 1

        vht = pd.DataFrame(
            (counts * travel_times).T @ aggregation_vector, columns=[f"vht_{i}" for i in range(0, new_num_steps)]
        )
        vmt = pd.DataFrame(
            (counts * lengths).T @ aggregation_vector, columns=[f"vmt_{i}" for i in range(0, new_num_steps)]
        )
        vht["vht_daily"] = vht.sum(axis=1) / 1000000
        vmt["vmt_daily"] = vmt.sum(axis=1) / 1000000

        return pd.concat([uuids, vht, vmt], axis=1).set_index("linknr")

    def get_flow_density(self):

        density = pd.DataFrame(
            self.get_array("link_moe", "link_density").T, columns=[f"density_{i}" for i in range(0, self.num_timesteps)]
        )
        flow = pd.DataFrame(
            self.get_array("link_moe", "link_out_flow_rate").T,
            columns=[f"flow_{i}" for i in range(0, self.num_timesteps)],
        )
        uuids = pd.Series(self.get_vector("link_moe", "link_uids"), name="linknr")

        lengths = pd.Series(self.get_vector("link_moe", "link_lengths"), name="length_m")

        return pd.concat([uuids, lengths, flow, density], axis=1).set_index("linknr")
