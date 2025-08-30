# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import copy
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from .add_missing import initialize_seed
from .validation import validate
from .verify_codes import verify_polaris_codes
from .verify_distribution_input import verify_veh_dist_input
from .verify_inputs import verify_inputs
from .verify_target_distribution import verify_target_distribution
from .verify_zones import verify_zone_input


class RedistributeVehicles:
    def __init__(
        self, model_dir, veh_file, target_file, veh_codes_file, zone_weights=None, fleet_mode=False  # noqa: C901
    ):
        """
        Update existing vehicle distribution files to new aggregate forecast targets
        :param model_dir:  The working directory where all files can be found
        :param veh_file:  existing vehicle distribution file with required field "TRACT", "POLARIS_ID", "VINTAGE" and "PROPORTION",
                          along with common fields from the control and vehicle_codes files
        :param target_file:  required aggregate distribution of vehicles types across control fields, with probability that sums to 1
        :param veh_codes_file:  Mapping of the control fields and other fields to POLARIS vehicle type values
        :param zone_weights:    Count of total vehicles by zone for the same zone system as in veh_file, if omitted makes all zones have equal weight in IPF
        :param conv_threshold:  When to stop the IPF process
        :return: None

        >>> model_dir = "C:/polaris_models/gpra/austin/built/veh_updates"
        >>> veh_file = "vehicle_distribution_updated_campo.txt"
        >>> target_file = "target_2035_low.csv"
        >>> veh_codes_file = "polaris_vehicle_codes.csv"
        >>> zone_weights = "veh_by_zone.csv"
        >>> conv_threshold = 0.001
        >>> regenerate_veh_dist_file(model_dir, veh_file, target_file, veh_codes_file, zone_weights, conv_threshold)
        """

        self.match_veh_type = 0
        self.match_zone = 0
        self.err = np.inf
        self.__results: pd.DataFrame
        self.fleet_mode = fleet_mode
        self.__final_columns = ["TRACT", "POLARIS_ID", "VEHICLE_CLASS", "FUEL", "POWERTRAIN", "VINTAGE", "PROPORTION"]
        # Polaris codes
        self.codes_df = pd.read_csv(Path(model_dir) / veh_codes_file)
        if self.codes_df.columns.size == 1:
            self.codes_df = pd.read_csv(Path(model_dir) / veh_codes_file, delimiter="\t")

        # get the vehicle distribution
        self.veh_df = pd.read_csv(Path(model_dir) / veh_file)
        if self.veh_df.columns.size == 1:
            self.veh_df = pd.read_csv(Path(model_dir) / veh_file, delimiter="\t")

        # Targets
        self.target_df = pd.read_csv(Path(model_dir) / target_file)
        if self.target_df.columns.size == 1:
            self.target_df = pd.read_csv(Path(model_dir) / target_file, delimiter="\t")

        self.pcode_idx = list(self.codes_df.columns[1:])

        self.controls = list(self.target_df.columns[:-1])
        t_names = {n: n.upper() for n in self.controls}
        self.controls = [x.upper() for x in self.controls]
        self.target_df.rename(columns=t_names, inplace=True)
        self.target_df.set_index(self.controls, inplace=True)

        # get the zone weights if requested or create default if not
        if self.fleet_mode:
            self.zone_df = None
        else:
            if zone_weights:
                self.zone_df = pd.read_csv(Path(model_dir) / zone_weights)
                if self.zone_df.columns.size == 1:
                    self.zone_df = pd.read_csv(Path(model_dir) / zone_weights, delimiter="\t")
            else:
                self.zone_df = self.veh_df.groupby("TRACT")[self.veh_df.columns[-1:]].count().reset_index()
                n = self.zone_df.columns[-1:][0]
                self.zone_df.rename(columns={n: "veh_count"}, inplace=True)
                self.zone_df["veh_count"] = 100.0

    def check_inputs(self):
        self.codes_df = verify_polaris_codes(self.codes_df)

        self.target_df = verify_target_distribution(self.target_df)

        self.veh_df = verify_veh_dist_input(self.veh_df, self.controls, self.fleet_mode)

        if not self.fleet_mode:
            self.zone_df = verify_zone_input(self.zone_df)

        verify_inputs(self.veh_df, self.target_df)

    def process(self, conv_threshold=0.001, max_iterations=50):
        self.check_inputs()

        default_values = {
            "VEHICLE_CLASS": "DEFAULT",
            "POWERTRAIN": "Conventional",
            "FUEL": "Gas",
            "AUTOMATION": np.nan,
            "CONNECTIVITY": "No",
            "VINTAGE": 0,
        }

        # Add any vehicle type combinations with default small probabilities from the target that are missing for each zone
        if not self.fleet_mode:
            self.veh_df = initialize_seed(self.veh_df, self.target_df, self.zone_df, self.codes_df, default_values)

        # add the default uncontrolled values for doing lookup in the polaris codes map
        pcode_missing_values = {}
        self.pcode_idx_names = copy.deepcopy(self.controls)
        source_names = []
        tottime = perf_counter()

        for c in self.pcode_idx:
            if c not in self.controls:
                self.pcode_idx_names.append(c)
            # add defaults for each uncontrolled vehicle characteristics to the source dataframe
            if c not in self.veh_df.columns:
                if c not in default_values:
                    print("ERROR, unknown vehicle characteristic dimension name '" + c)
                else:
                    pcode_missing_values[c] = default_values[c]
            else:
                source_names.append(c)

        # convert vehicle distribution to actual counts for use in IPF
        df = self.veh_df.join(self.zone_df, "TRACT")
        df["VEH_TOT"] = df["PROPORTION"] * df["veh_count"]

        # ------------ Do IPF to targets --------------------------------------------
        counter = 0
        while self.err > conv_threshold and counter < max_iterations:
            ttime = perf_counter()
            # IPF on vehicle self.controls dimension
            g_veh = df[self.controls + ["VEH_TOT"]].groupby(self.controls)
            agg_type = g_veh.sum() / df["VEH_TOT"].sum()
            veh_update = self.target_df.join(agg_type, self.controls)
            veh_update.loc[veh_update.VEH_TOT > 0, "value"] = veh_update["value"] / veh_update.VEH_TOT
            df = self.update_across_veh_types(df, veh_update)

            if self.fleet_mode:
                # If fleet mode, we can just exit now
                veh_update.loc[veh_update.VEH_TOT > 0, "value"] = veh_update["value"] / veh_update.VEH_TOT
                self.err = abs(1.0 - veh_update["veh_count"].max())
                break

            # IPF on zone count dimension
            g_cnt = df[["TRACT", "VEH_TOT"]].groupby(["TRACT"]).sum()
            cnt_update = g_cnt.join(self.zone_df, "TRACT")
            cnt_update["veh_count"] = cnt_update.veh_count.astype(np.float64)
            cnt_update.loc[cnt_update.VEH_TOT > 0, "veh_count"] = cnt_update.veh_count / cnt_update.VEH_TOT
            df = self.update_across_zones(df, cnt_update)
            self.err = abs(1.0 - cnt_update["veh_count"].max())

            counter += 1
            print(f"Iteration {counter}: {round(perf_counter() - ttime, 1)}s , error {round(self.err, 5)}")

        df["PROPORTION"] = df.apply(lambda x: self.update_prob(x), axis=1)

        df.dropna(subset=self.__final_columns, inplace=True)
        df = df[df.PROPORTION > 0]
        self.__results = df.set_index(self.__final_columns)
        self.__check_tract_totals()

        print(f"Total processing time: {round(perf_counter() - tottime, 1)}s")

    def save_results(self, out_veh_file):
        model_dir = Path(out_veh_file).parent
        self.match_veh_type, self.match_zone = validate(
            self.__results, self.target_df, self.zone_df, model_dir, out_veh_file
        )

        df = self.__results.reset_index()[self.__final_columns]

        df[df.PROPORTION > 0].to_csv(out_veh_file, index=False)

    def fix_across_tracts(self):
        df = self.__results.reset_index()
        df2 = df.groupby(["TRACT"]).sum()[["PROPORTION"]].rename(columns={"PROPORTION": "FACTOR"})
        df = df.set_index(["TRACT"]).join(df2)
        df.PROPORTION /= df.FACTOR
        df.PROPORTION.fillna(0)
        self.__results = df.reset_index().set_index(self.__final_columns)
        print("Proportions for missing tracts have been fixed")

    def __check_tract_totals(self):
        df = self.__results.reset_index()
        df2 = df.groupby(["TRACT"]).sum()[["PROPORTION"]]
        if round(df2.PROPORTION.max(), 4) > 1 or round(df2.PROPORTION.min(), 4) < 1:
            print("YOUR TRACT CONTROL TOTALS DO NOT ALL ADD TO 1.0 YOU MAY HAVE MISSING TRACTS ON YOUR CONTROL TOTALS")
            print("You can correct this issue by calling the method fix_across_tracts before saving results")

    def update_across_veh_types(self, df, update_values):
        df2 = df.set_index(self.controls)
        df3 = df2.join(update_values, how="left", rsuffix="_v")
        df3.loc[:, "VEH_TOT"] *= df3["value"]
        df3.VEH_TOT.fillna(0)
        return df3.reset_index()[df.columns]

    def update_across_zones(self, df: pd.DataFrame, update_values: pd.DataFrame) -> pd.DataFrame:
        cols = df.columns
        fac = update_values[["veh_count"]].rename(columns={"veh_count": "mult_factor"})
        df = df.merge(fac, left_on="TRACT", right_index=True)
        df.loc[:, "VEH_TOT"] *= df.mult_factor
        return df[cols]

    def update_prob(self, row):
        p = row["PROPORTION"]
        if not pd.isna(row["veh_count"]):
            p = row["VEH_TOT"] / row["veh_count"]
        return p
