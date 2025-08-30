# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import warnings
from os import PathLike
from typing import Optional, Tuple

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import pandas as pd
from polaris.prepare.popsyn.linker_file import LinkerFile
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.db_utils import read_sql
from polaris.utils.list_utils import first_and_only
from scipy.stats import linregress  # type: ignore


class PopsynComparator:
    # The id linking people and households is named household - this is hard-coded in the c++ code
    HHID = "household"
    # The id linking households to the seed data - this is hard-coded in the c++ code
    HH_SURVEY_ID = "hhold"
    # this id links people to households and is hard-coded in the c++ code
    PERSONID = "person"
    # this id links people to seed data and is hard-coded in the c++ code. Note this is 0-based per HH.
    PERSON_SURVEY_ID = "id"
    # the name popsyn_region comes from supply_db locations and refers to tract ids; puma_id is created below
    CENSUS_TRACT_ID = "popsyn_region"
    # because some of our models use state + puma as id but others use just puma numbers we need to normalise
    PUMA_ID = "puma_id"
    PUMA_TO_TRACT_URL = "https://www2.census.gov/geo/docs/maps-data/data/rel/2010_Census_Tract_to_2010_PUMA.txt"

    def __init__(
        self,
        result_dir: PathLike,
        sample_factor: float,
        linker_file: LinkerFile,
        db_name: Optional[str] = None,
    ):
        self.linker = linker_file
        self.polaris_inputs = PolarisInputs.from_dir(result_dir, db_name, use_parent_supply=True)
        # self.dir = Path(result_dir)
        self.sample_factor = sample_factor

        self.population = self.load_population(self.polaris_inputs)
        self.attach_geo_fields()

        self.replace_polaris_data_with_seed_data()

        self.population_for_control_variables = self.extract_population_for_control_variables()

    def replace_polaris_data_with_seed_data(self):
        hh_survey = pd.read_csv(self.linker.file["HH"], sep=",|\t", engine="python")
        hh_survey_id_col = hh_survey.columns[self.linker.seed_id["HH"]]

        hh_copy = self.population["HH"][
            [
                PopsynComparator.HHID,
                PopsynComparator.HH_SURVEY_ID,
                PopsynComparator.CENSUS_TRACT_ID,
                PopsynComparator.PUMA_ID,
            ]
        ].copy()

        hh_copy = hh_survey.merge(
            hh_copy, right_on=PopsynComparator.HH_SURVEY_ID, left_on=hh_survey_id_col, how="right", validate="1:m"
        )
        assert not hh_copy[hh_survey_id_col].isnull().any()
        self.population["HH"] = hh_copy

        ppl_survey = pd.read_csv(self.linker.file["PERSON"], sep=",|\t", engine="python")
        ppl_survey_id_col = ppl_survey.columns[self.linker.seed_id["PERSON"]]
        ppl_survey[PopsynComparator.PERSON_SURVEY_ID] = ppl_survey.groupby(ppl_survey_id_col).cumcount()

        ppl_copy = self.population["PERSON"][
            [
                PopsynComparator.PERSONID,
                PopsynComparator.PERSON_SURVEY_ID,
                PopsynComparator.HHID,
                PopsynComparator.CENSUS_TRACT_ID,
                PopsynComparator.PUMA_ID,
            ]
        ].merge(
            hh_copy[[PopsynComparator.HHID, PopsynComparator.HH_SURVEY_ID]],
            on=PopsynComparator.HHID,
            how="left",
            validate="m:1",
        )

        ppl_copy = ppl_survey.merge(
            ppl_copy,
            left_on=[ppl_survey_id_col, PopsynComparator.PERSON_SURVEY_ID],
            right_on=[PopsynComparator.HH_SURVEY_ID, PopsynComparator.PERSON_SURVEY_ID],
            how="right",
            validate="1:m",
        )
        assert not ppl_copy[ppl_survey_id_col].isnull().any()
        assert not ppl_copy[PopsynComparator.PERSON_SURVEY_ID].isnull().any()
        self.population["PERSON"] = ppl_copy

    def summarise(self):
        sf1 = pd.read_csv(self.linker.file["CONTROL"], sep=",|\t", engine="python")

        possible_num_hh_column_names = ["Households", "HOUSEHOLDS", "HH_COUNT"]
        hh_col = first_and_only([x for x in sf1.columns if x in possible_num_hh_column_names])

        possible_num_ppl_column_names = ["Persons", "PERSONS", "POP"]
        per_col = first_and_only([x for x in sf1.columns if x in possible_num_ppl_column_names])

        total_num_synthesized_households = self.population["HH"].shape[0] / self.sample_factor
        total_num_control_households = sf1[hh_col].sum()
        logging.info(
            f"Synthesized {total_num_synthesized_households / total_num_control_households:.2%} of households"
            + f" - synthesized = {total_num_synthesized_households:,.0f}, sf1 marginal = {total_num_control_households:,.0f}"
        )

        total_num_synthesized_people = self.population["PERSON"].shape[0] / self.sample_factor
        total_num_control_people = sf1[per_col].sum()
        logging.info(
            f"Synthesized {total_num_synthesized_people / total_num_control_people:.2%} of people    "
            + f" - synthesized = {total_num_synthesized_people:,.0f}, sf1 marginal = {total_num_control_people:,.0f}"
        )

    @staticmethod
    def load_population(files):
        return {
            "HH": read_sql("SELECT * FROM household", ScenarioCompression.maybe_extract(files.demand_db)),
            "PERSON": read_sql("SELECT * FROM person", ScenarioCompression.maybe_extract(files.demand_db)),
        }

    def locations_use_tract_ids(self):
        # figure out if demand_db / household home location field is at locations (POI) level or tract level
        # tract ids are integers that have been created via int(state_id + county_id + tract_id), where tract_id has
        # 6 digits, county_id 3 and state 1 or 2.
        # locations (POIs) have 1-based contiguous index, as long as there are less than 1e10 we can simply test
        # the length of the id to figure out what to do.
        # Note 'location' is name of location field as per c++ code
        if self.population["HH"].empty:
            return True
        if int(np.log10(self.population["HH"]["location"].max())) + 1 >= 10:
            logging.info(
                "It looks like HH home locations are at tract id level, so popsynth was run without location assignment"
            )
            return True
        return False

    def load_puma_to_tract_lu(self):
        # Now attach pumas based on tract ids. Important to specify dtype as string, they are zero-padded
        df = pd.read_csv(self.PUMA_TO_TRACT_URL, dtype=str)

        # puma_id and tract id (==GEOID) will be merged with polaris data, which is integer, so need to convert here
        if self.linker.puma_id_contains_state_id:
            df[PopsynComparator.PUMA_ID] = (df["STATEFP"] + df["PUMA5CE"]).astype(int)
        else:
            df[PopsynComparator.PUMA_ID] = df["PUMA5CE"].astype(int)

        df[PopsynComparator.CENSUS_TRACT_ID] = (df["STATEFP"] + df["COUNTYFP"] + df["TRACTCE"]).astype(np.float64)
        return df

    def attach_geo_fields(self):
        """ "
        popsynth marginals are at tract level, popsynth results at either location level or tract level.
        Seeds are provided at puma level so we attach these here too to compare results at more aggregate level.
        """

        # if home location is at POI level, we need to map these ids to census tracts.
        if self.locations_use_tract_ids():
            self.population["HH"] = self.population["HH"].rename(columns={"location": PopsynComparator.CENSUS_TRACT_ID})
        else:
            locations = read_sql(
                f"SELECT location, {PopsynComparator.CENSUS_TRACT_ID} FROM location",
                ScenarioCompression.maybe_extract(self.polaris_inputs.supply_db),
            )
            # locations are POIs, popsyn_region are census tract numbers generally (but can be updated).
            locations[PopsynComparator.CENSUS_TRACT_ID] = locations[PopsynComparator.CENSUS_TRACT_ID].astype(int)

            self.population["HH"] = self.population["HH"].merge(locations, on="location", how="left", validate="m:1")
            assert not self.population["HH"][PopsynComparator.CENSUS_TRACT_ID].isnull().any()

        self.population["HH"] = self.population["HH"].merge(
            self.load_puma_to_tract_lu()[[PopsynComparator.CENSUS_TRACT_ID, PopsynComparator.PUMA_ID]],
            on=PopsynComparator.CENSUS_TRACT_ID,
            how="left",
            validate="m:1",
        )

        # I found one nan in DFW with popsyn_region = 0 - drop these and warn
        no_location_filter = self.population["HH"][PopsynComparator.PUMA_ID].isnull()
        if no_location_filter.any():
            logging.warning(
                f"Found {no_location_filter.sum()} households without valid home puma"
                + ", dropping these now. popsyn_region ids for these should be zero, unique values found:"
                + f" {self.population['HH'][no_location_filter][PopsynComparator.CENSUS_TRACT_ID].unique()}"
            )
            self.population["HH"] = self.population["HH"][~no_location_filter]
            self.population["HH"][PopsynComparator.CENSUS_TRACT_ID] = self.population["HH"][
                PopsynComparator.CENSUS_TRACT_ID
            ].astype(int)

            self.population["PERSON"] = self.population["PERSON"].loc[
                self.population["PERSON"][self.HHID].isin(self.population["HH"][self.HHID])
            ]

        # make life easier by attaching geo columns to PEOPLE
        self.population["PERSON"] = self.population["PERSON"].merge(
            self.population["HH"][[self.HHID, PopsynComparator.CENSUS_TRACT_ID, PopsynComparator.PUMA_ID]],
            on=self.HHID,
            how="left",
            validate="m:1",
        )

    def extract_population_for_control_variables(self):
        rv = {
            type: {dim: {} for dim in range(len(self.linker.dimensions[type]))}
            for type in self.linker.control_data.keys()
        }

        for type in rv.keys():
            logging.debug(f"Extracting {type}")
            access_type = type  # name for synthetic population data table, TESTHH is part of HH
            if "TEST" in type:
                access_type = type[4:]

            for dim in rv[type].keys():
                logging.debug(f"  Extracting {type}[{dim}]")
                seed_index = self.linker.control_variables[type][dim].seed_index_column
                demand_name = self.population[access_type].columns[seed_index]
                synpop_data = self.population[access_type].loc[
                    :, [PopsynComparator.CENSUS_TRACT_ID, PopsynComparator.PUMA_ID, demand_name]
                ]

                for margvar_name, margvar_data in self.linker.control_data[type][dim].items():
                    logging.debug(f"Extracting {type}[{dim}] data for sf1 field {margvar_name}")
                    low_val = margvar_data["seed_data_min_val"]
                    high_val = margvar_data["seed_high_val_excl"]
                    rv[type][dim][margvar_name] = synpop_data.loc[
                        (synpop_data[demand_name] >= low_val) & (synpop_data[demand_name] < high_val)
                    ].astype(float)

        return rv

    @classmethod
    def plot_scatter(
        cls,
        comp: pd.DataFrame,
        title: Optional[str],
        plt_style: str = "tableau-colorblind10",
        figsize: Tuple[int, int] = (5, 5),
        ax=None,
    ):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                reg = linregress(comp[comp.columns[0]], comp[comp.columns[1]])
                ols_label = f"y ~ {reg.slope:.2f}x {reg.intercept:+.1f}, r^2={pow(reg.rvalue, 2):.3f}"
        except Exception:
            reg, ols_label = None, "Bad-fit for OLS"

        with plt.style.context(plt_style):  # type: ignore
            call_show = False
            if ax is None:
                _ = plt.figure(figsize=figsize)
                ax = plt.axes()
                call_show = True

            ax.scatter(
                comp[comp.columns[0]],
                comp[comp.columns[1]],
            )
            ax.text(
                0.03,
                0.97,
                ols_label,
                fontsize=10,
                horizontalalignment="left",
                verticalalignment="top",
                transform=ax.transAxes,
            )
            ax_limits = (comp.min().min() * 0.9, comp.max().max() * 1.03)
            ax.set_xlim(ax_limits)
            ax.set_ylim(ax_limits)
            ax.axline(xy1=(0, 0), slope=1, c="grey", linestyle="dotted", linewidth=0.5)
            reg and ax.axline(xy1=(0, reg.intercept), slope=reg.slope)
            ax.set_title(title, fontsize=8)
            call_show and plt.show(block=False)

    @classmethod
    def compare_synthpop_to_controls(
        cls,
        control_data,
        synth_data,
        sample_fac,
        geo_col_index,  # 0 for tract, 1 for region
        compare_name,
        plt_style: str = "tableau-colorblind10",
        figsize=(5, 5),
        ax=None,
    ):
        c_geo_col = control_data.columns[geo_col_index]
        p_geo_col = synth_data.columns[geo_col_index]

        comp = pd.merge(
            control_data.iloc[:, [geo_col_index, 2]].groupby(c_geo_col).sum().rename(columns=lambda x: "control"),
            synth_data.iloc[:, [geo_col_index, 2]].groupby(p_geo_col).size().to_frame("synthesized"),
            left_on=c_geo_col,
            right_on=p_geo_col,
            how="outer",
            validate="1:1",
        ).fillna(0)
        comp["synthesized"] /= sample_fac
        if ax is None:
            title = (
                f"{compare_name}: control = {comp['control'].sum():,}, synthetic population"
                + f" = {comp['synthesized'].sum():,.0f}"
            )
        else:
            title = compare_name
        PopsynComparator.plot_scatter(comp, title, plt_style, figsize, ax=ax)
        return comp

    def generate_comparison_plots(self, geo_level: int):
        assert geo_level in [0, 1], f"Need geo level 0 for tract or 1 for puma, not {geo_level}"

        # Figure out how many rows/cols we need in a facet-grid set of plots
        columns = sum(len(e) for e in self.population_for_control_variables.values())
        rows = max(
            len(self.linker.control_data[type][dim])
            for type, v in self.population_for_control_variables.items()
            for dim in v.keys()
        )
        fig, axes = plt.subplots(rows, columns, figsize=(4 * columns, 4 * rows))

        col_headers = []
        col_idx = 0
        for type, v in self.population_for_control_variables.items():
            for dim in v.keys():
                row_idx = 0
                col_headers.append(type)
                for margvar_name, margvar_data in self.linker.control_data[type][dim].items():
                    _ = PopsynComparator.compare_synthpop_to_controls(
                        margvar_data["control_data"],
                        self.population_for_control_variables[type][dim][margvar_name],
                        self.sample_factor,
                        geo_col_index=geo_level,
                        compare_name=margvar_name,
                        ax=axes[row_idx][col_idx],
                    )
                    row_idx += 1

                [axes[r][col_idx].axis("off") for r in range(row_idx, rows)]
                col_idx += 1

        fig.tight_layout()
        add_headers(fig, col_headers=col_headers, fontsize=12)

        plt.show(block=False)


def add_headers(
    fig, *, row_headers=None, col_headers=None, row_pad=1, col_pad=20, rotate_row_headers=True, **text_kwargs
):
    # Based on https://stackoverflow.com/a/25814386

    axes = fig.get_axes()

    for ax in axes:
        sbs = ax.get_subplotspec()

        # Putting headers on cols
        if (col_headers is not None) and sbs.is_first_row():
            ax.annotate(
                col_headers[sbs.colspan.start],
                xy=(0.5, 1),
                xytext=(0, col_pad),
                xycoords="axes fraction",
                textcoords="offset points",
                ha="center",
                va="baseline",
                **text_kwargs,
            )

        # Putting headers on rows
        if (row_headers is not None) and sbs.is_first_col():
            ax.annotate(
                row_headers[sbs.rowspan.start],
                xy=(0, 0.5),
                xytext=(-ax.yaxis.labelpad - row_pad, 0),
                xycoords=ax.yaxis.label,
                textcoords="offset points",
                ha="right",
                va="center",
                rotation=rotate_row_headers * 90,
                **text_kwargs,
            )
