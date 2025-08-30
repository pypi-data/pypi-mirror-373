# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
# matplotlib 3.8 should have type hints, until then we just ignore
from itertools import cycle
import logging
import math
import re
import traceback
from pathlib import Path
from re import Pattern
from typing import Optional
from uuid import uuid1

import numpy as np
import pandas as pd
import seaborn as sns

from polaris.analyze.result_kpis import ResultKPIs
from polaris.utils.pandas_utils import filter_df
from polaris.utils.plot_utils import filter_list_for_display, scatter_plot, extract_common_legend


# We have to delay importing of matplotlib as it causes CI problems for QPolaris
# import matplotlib.pyplot as plt  # type: ignore


class KpiComparator:
    """This class provides an easy way to group together multiple runs of POLARIS and compare their outputs. Runs KPIs are
    added along with a string based name which is used as the label for that run in any subsequent plots which are
    generated.

    ::

        from polaris.analyze.kpi_comparator import KpiComparator

        results = KpiComparator()
        results.add_run(ResultKPIs.from_iteration(ref_project_dir / f"{city}_iteration_2"), 'REF_iteration_2')
        results.add_run(ResultKPIs.from_iteration(eval_project_dir / f"{city}_iteration_2"), 'EVAL_iteration_2')

    Metric comparison plots can then be generated in a notebook using:

    ::

        results.plot_mode_share()
        results.plot_vmt()
        results.plot_vmt_by_link_type()

    Any number of runs can be added using `add_run` up to the limit of readability on the generated plots.

    The object can also be used to generate a set of csv files for input into Excel (if you really have to use Excel):

    ::

        results.dump_to_csvs(output_dir = "my_csv_dump_dir")
    """

    def __init__(self):
        import matplotlib.pyplot as plt

        plt.rc("axes", axisbelow=True)  # We want our grid lines to sit behind our chart elements

        self.runs = {}
        self.results = None

    def add_run(self, kpi: ResultKPIs, run_id: str):
        if kpi is None:
            return
        if run_id in self.runs:
            run_id = f"{run_id}-{str(uuid1())[0:6]}"
        self.runs[run_id] = kpi

    def has_run(self, run_id):
        return run_id in self.runs

    def dump_to_csvs(self, output_dir, metrics_to_dump=None, **kwargs):
        Path(output_dir).mkdir(exist_ok=True, parents=True)
        metrics = metrics_to_dump or ResultKPIs.available_metrics()
        metrics = set(metrics) - {"num_adults", "num_employed", "num_hh", "tts"}  # remove legacy scalar metrics
        for m in metrics:
            df = self._get_results(m, **kwargs)
            if df is not None and isinstance(df, pd.DataFrame):
                df.to_csv(Path(output_dir) / f"{m}.csv")

        return metrics

    def plot_everything(self, **kwargs):
        # import matplotlib.pyplot as plt

        exclusions = ["plot_multiple_gaps", "plot_everything"]
        plot_methods = [e for e in dir(self) if e.startswith("plot_") and e not in exclusions]
        for p in plot_methods:
            print(p)
            if callable(self.__getattribute__(p)):
                try:
                    fn = self.__getattribute__(p)
                    fn(**kwargs)
                    # plt.show()
                except Exception:
                    print(f"{p}: failed")

    @classmethod
    def available_plots(self):
        exclusions = ["plot_multiple_gaps", "plot_everything"]
        return [e.replace("plot_", "") for e in dir(self) if e.startswith("plot_") and e not in exclusions]

    def plot_mode_share(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("mode_shares", **kwargs)
        df = df[~(df["mode"].str.contains("FAIL") | df["mode"].str.contains("NO_MOVE"))]
        if df is None or df.empty:
            logging.warning("There were no results for 'mode_shares'")
            return
        for col in ["total_pr", "HBW_pr", "HBO_pr", "NHB_pr"]:
            df[col] *= 100.0

        def f(y, ax, title):
            sns.barplot(df, x="mode", y=y, hue="run_id", ax=ax)
            ax.set_ylabel(f"Proportion (%) of {title} trips")
            ax.set_xlabel(None)
            ax.set_ylim([0, 90])
            KpiComparator._style_axes([ax], rotate_x_labels=False)

        if "group_by" in kwargs:
            del kwargs["df"]
            mode = kwargs.get("mode", "SOV")
            fig, axes, legend = self.across_iterations(
                {
                    "total_pr": "Total",
                    "HBW_pr": "Home Based Work",
                    "HBO_pr": "Home Based Other",
                    "NHB_pr": "Non Home Based",
                },
                separate_legend=False,
                df=df[df["mode"] == mode],
                **kwargs,
            )
            plt.suptitle(f"Mode Choice ({mode}) by {kwargs['group_by']}", fontsize=20)
        else:
            fig, axes = plt.subplots(2, 2, figsize=(20, 10), sharex="all")
            f("total_pr", axes[0, 0], title="Total")
            axes[0, 0]
            f("HBW_pr", axes[1, 0], title="HBW")
            f("HBO_pr", axes[0, 1], title="HBO")
            f("NHB_pr", axes[1, 1], title="NHB")

            KpiComparator._style_axes(
                np.ravel(axes),
                rotate_x_labels=60,
                fontsize=10,
                common_legends=True,
                suptitle="Mode Share by Activity Type",
            )
            fig.subplots_adjust(hspace=0.1)  # , top=0.92)

        return fig

    def plot_population(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("population", **kwargs)
        df.rename(columns={"num_persons": "population"})
        fig, ax = plt.subplots(figsize=(5, 5))
        _ = sns.barplot(ax=ax, data=df, hue=kwargs.get("hue", "run_id"), y="num_persons")
        leg = KpiComparator._style_axes([ax], rotate_x_labels=False, common_legends=True, suptitle="Population")
        leg.set_bbox_to_anchor([1.3, 0.5])  # Move the legend to the right hand side
        return fig

    def plot_congestion_pricing(self, **kwargs):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(5, 5))
        df = self._get_results("road_pricing", **kwargs).reset_index(drop=True)
        sns.barplot(ax=ax, data=df, x="run_id", y="total_toll")
        ax.set_ylabel("Revenue ($)")
        ax.set_label(None)
        KpiComparator._style_axes([ax], rotate_x_labels=45, suptitle="Congestion Pricing Revenue")

        return fig

    def plot_transit(self, **kwargs):
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
        df = self._get_results("transit_boardings", **kwargs)
        df["mode-agency"] = df["mode"] + "-" + df["agency"]
        sns.barplot(data=df, x="mode-agency", y="boardings", hue="run_id", errorbar=None, ax=axes[0])
        sns.barplot(data=df, x="mode-agency", y="alightings", hue="run_id", errorbar=None, ax=axes[1])
        suptitle = "Board/Alightings by Mode & Agency"
        KpiComparator._style_axes(axes, rotate_x_labels=20, common_legends=True, suptitle=suptitle)
        axes[1].set_xlabel(None)
        fig.subplots_adjust(hspace=0.1)  # , top=0.92)
        return fig

    def add_iter(self, x):
        if isinstance(x, pd.DataFrame):
            x["iter"] = x.run_id.str.replace(".*_iteration_", "", regex=True)
        else:
            raise RuntimeError(f"Unknown argument type for add_iter: {type(x)}")
        return x

    def across_iterations(self, cols, **kwargs):
        import matplotlib.pyplot as plt

        df = kwargs["df"]
        x_col = kwargs.get("x", "iter")
        if x_col == "iter" and x_col not in df.columns:
            df = self.add_iter(df)
        group_col = kwargs["group_by"]
        groups = df[group_col].unique()
        colors = cycle(sns.color_palette("colorblind") + sns.color_palette("pastel") + sns.color_palette("bright"))
        marker = kwargs.get("marker", "")

        separate_legend = int(kwargs.get("separate_legend", True))
        num_plots = len(cols) + separate_legend
        num_rows = math.ceil(num_plots / 2)
        fig, axes = plt.subplots(num_rows, 2, figsize=(15, 6 * num_rows))
        axes = axes.flatten()

        legend = []

        # Add a dummy line using ALL the available x values (in case there are missing values in a group)
        x = sorted(df[x_col].unique())
        dummy_lines = [
            axes[i + separate_legend].plot(x, df[col].mean() * np.ones_like(x, dtype=np.float32))
            for i, col in enumerate(cols.keys())
        ]

        agg = kwargs["agg"] if "agg" in kwargs else dict.fromkeys(cols.keys(), "mean")

        # For each identified group...
        for g, color in zip(groups, colors):
            # Filter to just the given group, then average across each unique x-value
            df_ = df[df[group_col] == g].groupby(x_col).agg(agg).reset_index().sort_values(x_col)
            df_.columns = [c if isinstance(c, str) else re.sub(r"_$", "", "_".join(c).strip()) for c in df_.columns]

            # Add a line to each subplot for the current grouping
            for i, col in enumerate(cols.keys()):
                idx = i + separate_legend
                column_name = [e for e in [col, f"{col}_mean"] if e in df_.columns]
                (line,) = axes[idx].plot(df_[x_col], df_[column_name], color=color, marker=marker)
                if f"{col}_max" in df_ and f"{col}_min" in df_:
                    axes[idx].fill_between(x, df_[f"{col}_min"], df_[f"{col}_max"], color=color, alpha=0.2)
                    axes[idx].plot(df_[x_col], df_[f"{col}_min"], color=color, alpha=0.3, linestyle="--")
                    axes[idx].plot(df_[x_col], df_[f"{col}_max"], color=color, alpha=0.3, linestyle="--")

            legend += [(line, g)]

        # Remove the dummy lines
        [line[0].remove() for line in dummy_lines]

        # Set titles for each subplot
        for i, title in enumerate(cols.values()):
            axes[i + separate_legend].set_ylabel(title)
            axes[i + separate_legend].set_xlabel(x_col)

        # Use top left sub-plot for legend and style the axes
        legend_fontsize = np.interp(len(legend), [4, 12], [16, 10], left=16, right=10)
        if separate_legend:
            axes[0].legend(
                [e[0] for e in legend], [e[1] for e in legend], loc="center", ncol=3, fontsize=legend_fontsize
            )
            axes[0].set_axis_off()
        else:
            # Otherwise put the legend at the bottom of the figure and increase the spacing
            fig.legend(
                [e[0] for e in legend], [e[1] for e in legend], loc="lower center", ncol=4, fontsize=legend_fontsize
            )
        fig.subplots_adjust(bottom=0.2)

        KpiComparator._style_axes(axes[separate_legend:], rotate_x_labels=60)

        return fig, axes, legend

    def plot_act_dist(self, act_type: Optional[str] = None, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("activity_distances", **kwargs)

        if act_type is not None:
            df = df[df["acttype"].str.upper() == act_type.upper()]
        if df is None or df.empty:
            logging.warning("There were no results for 'activity_distances'")
            return

        if "group_by" in kwargs:
            kwargs["df"] = df
            fig, axes, legend = self.across_iterations(
                {"ttime_avg": "Travel Time (min)", "dist_avg": "Distance (miles)", "count": "Count"},
                agg={"ttime_avg": "mean", "dist_avg": "mean", "count": "sum"},
                **kwargs,
            )
            return fig
        else:
            fig, axes = plt.subplots(1, 3, figsize=(28, 5))
            sns.barplot(ax=axes[0], data=df, x="acttype", y="ttime_avg", hue="run_id")
            axes[0].legend([], [], frameon=False)
            axes[0].set_ylabel("Travel Time (min)")
            sns.barplot(ax=axes[1], data=df, x="acttype", y="dist_avg", hue="run_id")
            axes[1].legend([], [], frameon=False)
            axes[1].set_ylabel("Distance (miles)")
            sns.barplot(ax=axes[2], data=df, x="acttype", y="count", hue="run_id")
            axes[2].set_ylabel("Trip Count")
            KpiComparator._style_axes(axes, rotate_x_labels=60, suptitle="Activity Distributions")
            return fig

    def plot_vmt(self, **kwargs):
        if "df" not in kwargs:
            df = self._get_results("vmt_vht", **kwargs).reset_index()

            if "mode" in kwargs:
                df = filter_df(df, {"mode": kwargs["mode"]})

            if df is None or df.empty:
                logging.warning("There were no results for 'vmt'")
                return

            df = df[~(df["mode"].str.contains("FAIL") | df["mode"].str.contains("NO_MOVE"))]
            kwargs["df"] = df.groupby(["mode", "run_id"]).sum().reset_index()

        kwargs["group_by"] = kwargs.get("group_by", "mode")
        cols = {"million_VMT": "VMT (millions)", "speed_mph": "Speed (mi/h)", "count": "Number of trips"}
        kwargs["agg"] = {"million_VMT": "sum", "speed_mph": "mean", "count": "sum"}
        fig, axes, legend = self.across_iterations(cols, **kwargs)

        return fig

    def plot_vehicle_connectivity(self, **kwargs):
        import matplotlib.pyplot as plt

        df_veh_tech = self._get_results("vehicle_technology", **kwargs)

        # Add a passenger/truck designation column
        df_veh_tech["fleet_type"] = "passenger"
        df_veh_tech.loc[df_veh_tech.class_type.str.startswith("TRUCK"), "fleet_type"] = "truck"

        # Figure out the percentage (relative to the total pass/truck vehicles for that run) for each row
        group_by_key = kwargs.get("group_by", "run_id")

        # Calculate the proportion of the total (passenger or truck) fleet that each row representes
        key = ["fleet_type", "run_id"]
        df_veh_tech["proportion"] = (
            100.0 * df_veh_tech["veh_count"] / df_veh_tech.groupby(key)["veh_count"].transform("sum")
        )

        _, axes = plt.subplots(1, 1, figsize=(10, 5))
        df_veh_tech["connectivity"] = "Not Connected"
        df_veh_tech.loc[df_veh_tech.connected == "Yes", "connectivity"] = "Connected"

        x_col = kwargs.get("x", "run_id")
        df_ = df_veh_tech.groupby(list({x_col, "connectivity", group_by_key, "fleet_type"})).agg({"proportion": "sum"})
        df_ = df_.reset_index()

        df_["proportion"] = 100.0 - df_["proportion"]
        fig = sns.lineplot(df_, x=x_col, y="proportion", hue=group_by_key, ax=axes, style="fleet_type")
        fig.legend(loc="center left", bbox_to_anchor=(1.05, 0.5), ncol=1)

        axes.set_title("Proportion of Connected Vehicles within Fleet")
        axes.set_ylabel("Proportion (%)")

    @staticmethod
    def _style_axes(
        axes,
        grid=True,
        rotate_x_labels=False,
        fontsize=14,
        titles=None,
        suptitle=None,
        common_legends=False,
        ncol=4,
        legend_loc="lower center",
        legend_anchor=None,
        leg_base_height=0.7,
    ):
        legend = None
        for ax in axes:
            if grid:
                ax.grid(True, which="both", axis="y", color="#000000", alpha=0.15, zorder=0)
            if rotate_x_labels:
                ax.tick_params(axis="x", rotation=rotate_x_labels)
            if fontsize is not None:
                ax.tick_params(axis="x", labelsize=fontsize)
                ax.set_title(ax.get_title(), fontsize=fontsize + 2)
            ax.set_ylim(bottom=0)

        if titles is not None:
            [ax.set_title(title) for (ax, title) in zip(axes, titles)]
        if common_legends:
            extract_common_legend(axes, ncol, legend_loc, legend_anchor, leg_base_height)
        if suptitle is not None:
            import matplotlib.pyplot as plt

            plt.suptitle(suptitle, fontsize=20)
        return legend

    @staticmethod
    def _style_target_bars(patches):
        import matplotlib.pyplot as plt

        plt.setp(patches, linewidth=2, edgecolor="#000000aa", zorder=2, facecolor="#ffffff11", linestyle="--")

    def plot_vmt_by_link_type(self, **kwargs):
        import matplotlib.pyplot as plt

        if (df := self._get_results("vmt_vht_by_link", **kwargs)) is None:
            logging.info("No data for vmt_vht_by_link")
            return

        df = df.groupby(["type", "run_id"]).sum().reset_index()
        df = df[~df.type.isin(["BUSWAY", "EXTERNAL"])]

        def add_speed(label, hours):
            vmt = df[[f"vmt_{i}" for i in hours]]
            vht = df[[f"vht_{i}" for i in hours]]
            df[f"speed_{label}"] = vmt.sum(axis=1) / vht.sum(axis=1)

        add_speed("daily", ["daily"])
        add_speed("am_peak", [6, 7, 8])
        add_speed("pm_peak", [15, 16, 17])
        add_speed("off_peak", set(range(0, 24)) - {6, 7, 8} - {15, 16, 17})

        fig, axes = plt.subplots(2, 2, figsize=(15, 9), sharex=True)
        axes = np.ravel(axes)
        _ = sns.barplot(df, x="type", y="vmt_daily", hue="run_id", ax=axes[0], errorbar=None)
        _ = sns.barplot(df, x="type", y="speed_off_peak", hue="run_id", ax=axes[1], errorbar=None)
        _ = sns.barplot(df, x="type", y="speed_am_peak", hue="run_id", ax=axes[2], errorbar=None)
        _ = sns.barplot(df, x="type", y="speed_pm_peak", hue="run_id", ax=axes[3], errorbar=None)

        axes[0].set_ylabel("Daily VMT")
        axes[1].set_ylabel("Offpeak Speed (mi/h)")
        axes[2].set_ylabel("AM-Peak Speed (mi/h)")
        axes[2].set_xlabel(None)
        axes[3].set_ylabel("PM-Peak Speed (mi/h)")
        axes[3].set_xlabel(None)

        suptitle = "VMT & Speed by Link Type"
        KpiComparator._style_axes(axes, rotate_x_labels=30, common_legends=True, suptitle=suptitle)
        fig.subplots_adjust(hspace=0.08)  # top=0.92)

        return fig

    def plot_fundamental_diagram(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("flow_density_fd", **kwargs)

        if df is None or df.empty:
            logging.warning("No flow density data for this run")
            return

        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16, 6), sharey=True)
        suptitle = "Flow-Density Relationship"

        sns.scatterplot(
            df[df.type_x.str.contains("FREEWAY|EXPRESSWAY")], x="density_bin", y="flow", hue="run_id", ax=axs[0]
        )
        axs[0].set_ylabel("Flow rate (in veh/hr/lane)", fontsize=14)
        axs[0].set_xlabel("Density (in veh/mi/lane)", fontsize=14)

        sns.scatterplot(df[df.type_x == "MAJOR"], x="density_bin", y="flow", hue="run_id", ax=axs[1])
        axs[1].set_ylabel("Flow rate (in veh/hr/lane)", fontsize=14)
        axs[1].set_xlabel("Density (in veh/mi/lane)", fontsize=14)

        if "xlim" in kwargs:
            xlim = kwargs.get("xlim")
            axs[0].set_xlim([0, xlim])
            axs[1].set_xlim([0, xlim])

        KpiComparator._style_axes(
            axs,
            rotate_x_labels=0,
            fontsize=16,
            common_legends=True,
            suptitle=suptitle,
            titles=["Freeways", "Major Arterials"],
        )

        fig.subplots_adjust(top=0.9)

        return fig

    def plot_gaps(self, type="defult", **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("gaps", **kwargs)
        if df is None or df.empty:
            logging.warning("No gap data for this run")
            return

        x_col = kwargs.get("x", "iter")
        if x_col == "iter" and "iter" not in df.columns:
            df = self.add_iter(df)
        hue = kwargs.get("hue", None)
        id_vars = {e for e in ["run_id", x_col, hue] if e}
        df = pd.melt(df, id_vars=id_vars, var_name="gap_type", value_name="gap")
        df = df[df.gap_type.str.contains("relative_gap") & ~df.gap_type.str.contains("all_good")]
        if type == "all_good":
            df = df[df.gap_type.str.contains("relative_gap")]
        elif type == "all":
            df = df[df.gap_type.str.contains("relative_gap") & ~df.gap_type.str.contains("all_good")]

        fig = plt.figure(figsize=(16, 6))
        ax = fig.gca()

        sns.lineplot(df, x=x_col, y="gap", hue=hue, style="gap_type", ax=ax, errorbar=None)
        ax.set_xlabel(x_col)
        suptitle = "Gaps (styled by gap_type)"

        KpiComparator._style_axes([ax], rotate_x_labels=30, common_legends=True, suptitle=suptitle, leg_base_height=1.1)
        return fig

    @staticmethod
    def plot_multiple_gaps(kpi_results):
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(16, 6))
        colors = sns.color_palette(n_colors=len(kpi_results))
        i = 0
        for id, k in ((id, k) for id, k in kpi_results.items() if k is not None):
            df = k._get_results("gaps", False, False)
            if df is None:
                logging.error("df is None?")
                continue
            df = df.sort_values("run_id")
            fig.gca().plot(df["run_id"], df["relative_gap"], color=colors[i], marker="o", label=id)
            i = i + 1
        fig.gca().grid(True, which="both", color="#000000", alpha=0.2)
        return fig

    def plot_congestion_removal(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("gaps", **kwargs)
        if df is None or df.empty:
            logging.warning("No gap data for this run")
            return
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 6))
        colors = sns.color_palette(n_colors=3)
        sns.lineplot(df, x="run_id", y="congestion_removal", color=colors[0], marker="o")
        suptitle = "Congestion Removal"
        KpiComparator._style_axes([ax], rotate_x_labels=30, suptitle=suptitle)
        ax.set_ylabel("# Trips removed due to congestion")
        return fig

    def plot_trips_with_path(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("gaps", **kwargs)
        if df is None or df.empty:
            logging.warning("No gap data for this run")
            return

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8), sharey=False)
        colors = sns.color_palette(n_colors=3)
        sns.lineplot(data=df, x="run_id", y="trips_with_path", color=colors[0], marker="o", ax=ax[0], label="has_path")
        sns.lineplot(
            data=df, x="run_id", y="trips_without_path", color=colors[1], marker="o", ax=ax[0], label="no_path"
        )
        ax[0].legend()
        ax[0].set_ylabel("Trip Count")

        sns.lineplot(
            data=df,
            x="run_id",
            y="avg_experienced_gap_has_path",
            color=colors[0],
            marker="o",
            ax=ax[1],
            label="has_path",
        )
        sns.lineplot(
            data=df, x="run_id", y="avg_experienced_gap_no_path", color=colors[1], marker="o", ax=ax[1], label="no_path"
        )
        ax[1].legend()
        ax[1].set_ylabel("Average Experienced Gap")

        suptitle = "Trips With vs Without Path"
        KpiComparator._style_axes(ax, rotate_x_labels=30, suptitle=suptitle)

        return fig

    def _plot_in_network_variable(self, column_name, **kwargs):
        import matplotlib.pyplot as plt

        # this has a problem if there are missing values in the summary file, filter to X to select only the bits that exist for all summary files
        df = self._get_results("summary", **kwargs)
        df = df[df.simulated_time < 86340]
        df.sort_values(["run_id", "simulated_time"], inplace=True)

        if column_name not in df.columns:
            logging.error(f"Column {column_name} not found in summary file")
            return

        fig = plt.figure(figsize=(16, 6))
        run_ids = sorted(df.run_id.unique())
        colors = sns.color_palette("blend:#7AB,#EDA", n_colors=len(run_ids))

        colors = sns.color_palette("flare", n_colors=len(run_ids))
        colors = sns.color_palette("light:#5A9", n_colors=len(run_ids))

        for run_id, color in zip(run_ids, colors):
            df_ = df[df.run_id == run_id]
            fig.gca().plot(df_["simulated_time"] / 3600, df_[column_name], color=color)

        ax = fig.gca()
        title = column_name.replace("_", " ").title()
        KpiComparator._style_axes([ax], rotate_x_labels=False, suptitle=title)
        ax.legend(run_ids)
        ax.set_xlabel("Simulation Hour of Day")
        return fig

    def plot_pax_in_network(self, **kwargs):
        return self._plot_in_network_variable("pax_in_network", **kwargs)

    def plot_veh_in_network(self, **kwargs):
        return self._plot_in_network_variable("in_network", **kwargs)

    def plot_freight_in_network(self, **kwargs):
        return self._plot_in_network_variable("freight_in_network", **kwargs)

    def plot_cpu_mem(self, **kwargs):
        if (df := self._get_results("summary", **kwargs)) is None:
            logging.info("No summary file data available")
            return

        # df = df[["simulated_time", "wallclock_time(ms)", "physical_memory_usage", "run_id"]].copy()
        df.loc[:, "hour"] = df["simulated_time"] / 3600
        df.loc[:, "runtime"] = df["wallclock_time(ms)"] / 1000
        kwargs["df"] = df
        kwargs["agg"] = {"runtime": ["mean", "min", "max"], "physical_memory_usage": ["mean", "min", "max"]}
        kwargs["group_by"] = kwargs.get("group_by", "run_id")
        kwargs["x"] = kwargs.get("x", "hour")

        fig, axes, legend = self.across_iterations(
            {"runtime": "Runtime (s)", "physical_memory_usage": "Peak memory (MB)"}, separate_legend=False, **kwargs
        )
        axes[0].set_xlabel("Simulation Hour of Day", fontsize=10)
        axes[1].set_xlabel("Simulation Hour of Day", fontsize=10)
        fig.suptitle("Runtime and Memory usage", fontsize=20)
        fig.subplots_adjust(bottom=0.27)

        return fig

    def plot_polaris_exe(self, **kwargs):
        df = self._get_results("polaris_exe", **kwargs).drop(columns=["sha"])

        def make_clickable(val):
            # target _blank to open new window
            sha = val.split("/")[-1]
            return f'<a target="_blank" href="{val}">{sha}</a>'

        from IPython.display import display, HTML

        display(HTML("<h2>Polaris Executable Git Versions</h2>"))
        display(df.style.format({"url": make_clickable}))

    def plot_network_gaps(self, **kwargs):
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        df = self._get_results("network_gaps_by_link_type", **kwargs)
        sns.barplot(df, x="link_type", y="abs_gap", hue="run_id", ax=axes[0, 0], errorbar=None)
        sns.barplot(df, x="link_type", y="gap", hue="run_id", ax=axes[1, 0], errorbar=None)
        axes[0, 0].set_xlabel(None)

        df = self._get_results("network_gaps_by_hour", **kwargs)
        df.fillna(0.0, inplace=True)  # early morning hours have some weird values
        sns.lineplot(df, x="hour", y="abs_gap", hue="run_id", ax=axes[0, 1], errorbar=None)
        sns.lineplot(df, x="hour", y="gap", hue="run_id", ax=axes[1, 1], errorbar=None)
        axes[0, 1].set_xlabel(None)
        axes[1, 0].set_xlabel(None)
        axes[0, 0].sharex(axes[1, 0])  # manually share the axis for the left side pair
        axes[0, 1].sharex(axes[1, 1])
        axes[0, 0].tick_params(labelbottom=False)
        axes[0, 1].tick_params(labelbottom=False)
        fig.subplots_adjust(hspace=0.1, top=0.92, bottom=0.15)

        suptitle = "Gaps by Link Type (left) and by Hour (right)"
        KpiComparator._style_axes(np.ravel(axes), rotate_x_labels=45, suptitle=suptitle, common_legends=True)
        return fig

    def plot_skim_stats(self, show_min_max=False, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("skim_stats", **kwargs)
        df.sort_values("interval", inplace=True)
        if df is None or df.empty:
            logging.warning("No skim stats to plot")
            return

        def f(metric, mode, ax, ylabel):
            df_ = df[(df.metric == metric) & (df["mode"] == mode)]
            run_ids = df.run_id.unique()
            colors = sns.color_palette(n_colors=len(run_ids))
            line_width = 3
            for run_id, color in zip(run_ids, colors):
                df__ = df_[df_.run_id == run_id]
                x = (df__["interval"] / 60).astype(int)

                ax.plot(x, df__["avg"], linestyle="-", color=color, label=run_id, linewidth=line_width)
                line_width -= 0.5
                if show_min_max:
                    ax.plot(x, df__["min"], linestyle="--", color=color)
                    ax.plot(x, df__["max"], linestyle="--", color=color)
            ax.legend()
            ax.set_xticks(x)
            ax.set_ylabel(ylabel)

        def do(thing):
            return df[(df.metric == thing[0]) & (df["mode"] == thing[1])].shape[0] > 0

        things = [
            ("time", "Auto", "Time (min)"),
            ("distance", "Auto", "Distance (m)"),
            ("time", "Bus", "Bus Time (min)"),
            ("time", "Rail", "Rail Time (min)"),
        ]
        things = [thing for thing in things if do(thing)]

        fig, axes = plt.subplots(len(things), 1, figsize=(20, len(things) * 4), sharex=True)
        for (metric, mode, label), ax in zip(things, axes):
            f(metric, mode, ax, label)

        suptitle = "Average Skim value by hour"
        if show_min_max:
            suptitle += " (min/max dashed)"
        KpiComparator._style_axes(axes, suptitle=suptitle, common_legends=True)
        fig.subplots_adjust(top=0.92)
        return fig

    def plot_trip_length_distributions(self, max_dist=None, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("trip_length_distribution", **kwargs)
        if df is None or df.empty:
            logging.warning("No TLfD stats to plot")
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        for run_id in df.run_id.unique():
            df_ = df[df.run_id == run_id]
            df_ = df_.sort_values(by="distance")

            # For large models, using 200 to 400 bins yields much better curves
            ax.plot(df_.distance, df_.trips, label=run_id)

        if max_dist is not None:
            ax.set_xlim(0, max_dist)

        ax.legend(loc="upper right")
        ax.set(title="Trip length distribution")
        ax.set_xlabel("Trip length (km)")
        ax.set_ylabel("Trips")
        return fig

    def plot_activity_start_time_distributions(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("activity_start_time_distributions", **kwargs)

        if df.trip_start.max() < 20 * 3600:  # handle a bug in trip metrics calculation (remove in 2026)
            df.trip_start *= 1000 / 3600
        else:
            df.trip_start /= 3600

        if df is None or df.empty:
            logging.warning("No trip departure time data to plot")
            return

        fig, ax = plt.subplots(figsize=(13, 6))
        for run_id in df.run_id.unique():
            df_ = df[df.run_id == run_id]
            df_ = df_.sort_values(by="trip_start")

            # For large models, using 200 to 400 bins yields much better curves
            ax.plot(df_.trip_start, df_.trips, label=run_id)

        ax.set_xlabel(None)  # "Hour of day")
        ax.set_ylabel("Trip Count")

        KpiComparator._style_axes(
            [ax],
            common_legends=True,
            suptitle="Activity Start Time distribution",
            ncol=2,
            legend_anchor=[0.9, 0.5],
            legend_loc="upper left",
        )

        return fig

    def plot_planned_activity_start_time_distributions(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("planned_activity_start_time_distributions", **kwargs)
        df.activity_start /= 3600

        if df is None or df.empty:
            logging.warning("No trip departure time data to plot")
            return

        fig, ax = plt.subplots(figsize=(13, 6))
        for run_id in df.run_id.unique():
            df_ = df[df.run_id == run_id]
            df_ = df_.sort_values(by="activity_start")

            # For large models, using 200 to 400 bins yields much better curves
            ax.plot(df_.activity_start, df_.activities, label=run_id)

        ax.set_xlabel(None)  # "Hour of day")
        ax.set_ylabel("Activity Count")

        KpiComparator._style_axes(
            [ax],
            common_legends=True,
            suptitle="Planned Activity Start Time distribution",
            ncol=2,
            legend_anchor=[0.9, 0.5],
            legend_loc="upper left",
        )

        return fig

    def plot_tnc(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("tnc_request_stats", **kwargs)
        df["operator_mode"] = df["tnc_operator"] + "-mode_" + df["service_mode"].astype(str)

        if df is None or df.empty:
            logging.warning("There were no results for 'tnc_request_stats'")
            return

        fig, axes = plt.subplots(1, 3, figsize=(20, 8))

        def f(y, ax, title, ylabel):
            sns.barplot(df, x="operator_mode", y=y, hue="run_id", ax=ax)
            ax.set(title=title)
            ax.set_xlabel(None)
            ax.set_ylabel(ylabel)

        f("demand", axes[0], title="Demand", ylabel="trips")
        f("wait", axes[1], title="Wait time", ylabel="hours")
        f("ivtt", axes[2], title="IVTT", ylabel="hours")
        KpiComparator._style_axes(np.ravel(axes), rotate_x_labels=30, common_legends=True)
        return fig

    def plot_rmse_vs_observed(self, **kwargs):
        things = ["activity", "mode", "mode_boardings", "destination", "timing"]
        titles = {
            "activity": "Activity Generation",
            "mode": "Mode Share",
            "mode_boardings": "Mode Boardings",
            "destination": "TTime by Activity",
            "timing": "Departure Time",
        }
        df = self._get_results("rmse_vs_observed", **kwargs)
        return self.__rmse_vs_observed(things, titles, df)

    def plot_planned_rmse_vs_observed(self, **kwargs):
        things = ["activity", "mode", "timing"]
        titles = {
            "activity": "Activity Generation",
            "mode": "Mode Share",
            "timing": "Departure Time",
        }
        df = self._get_results("planned_rmse_vs_observed", **kwargs)
        return self.__rmse_vs_observed(things, titles, df)

    def __rmse_vs_observed(self, things, titles, df):
        import matplotlib.pyplot as plt

        if df is None or df.empty:
            logging.warning("There were no results for RMSEs")
            return

        def f(y, ax, title):
            sns.barplot(df, hue="run_id", y=y, ax=ax)
            ax.set(xlabel=None, ylabel=None)
            ax.set_title(title, fontsize=12, loc="center", y=-0.05)

        things = [y for y in things if df[f"RMSE_{y}"].max() > 0]

        fig, axes = plt.subplots(nrows=1, ncols=len(things), figsize=(20, 8), sharey=True)
        for y, ax in zip(things, axes):
            f(f"RMSE_{y}", ax, title=titles[y])
        suptitle = "RMSE against calibration targets"
        KpiComparator._style_axes(axes, rotate_x_labels=30, fontsize=None, common_legends=True, suptitle=suptitle)
        fig.subplots_adjust(top=0.92)
        return fig

    def _overlay_barplots(self, df, x_col, ax, title):
        exemplar_run_id = df.run_id.unique()[0]
        sns.barplot(
            data=df[df.run_id == exemplar_run_id],
            x=x_col,
            y="target",
            errorbar=None,
            color="white",
            width=0.85,
            ax=ax,
            estimator=np.sum,
        )
        KpiComparator._style_target_bars(ax.patches)
        sns.barplot(data=df, x=x_col, y="simulated", hue="run_id", errorbar=None, ax=ax, width=0.75, estimator=np.sum)
        if title is not None and title != "":
            ax.set(title=title, xlabel=None, ylabel=None)
        else:
            ax.set(xlabel=None, ylabel=None)

    def plot_calibration_for_activity_generation(self, df, **kwargs):
        df = self._get_results("calibration_act_gen", **kwargs)
        self.__calibration_for_activity_generation(df, title="Activity Generation Validation")

    def plot_planned_calibration_for_activity_generation_planned(self, df, **kwargs):
        df = self._get_results("calibration_act_gen_planned", **kwargs)
        self.__calibration_for_activity_generation(df, title="Planned Activity Generation Validation")

    def __calibration_for_activity_generation(self, df, title):
        import matplotlib.pyplot as plt

        if df is None or df.empty:
            logging.warning("There were no results for calibrating activity generation")
            return

        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
        self._overlay_barplots(df, "pertype", axes[0], "By Person Type")

        if "per_count" in df:
            # Generating a average trip rate (across the entire population) by activity type
            # isn't as easy as the above, we have to transform back to trip counts so that we get
            # our averaging correct.
            df["target"] *= df["per_count"]
            df["simulated"] *= df["per_count"]

            # We then div by the total number of people to get the average per person
            total_persons = df.groupby("pertype")["per_count"].mean().sum()
            df = df.groupby(["run_id", "acttype"])[["target", "simulated"]].sum() / total_persons
            self._overlay_barplots(df.reset_index(), "acttype", axes[1], "By Activity Type")

        fig.subplots_adjust(hspace=0.35)
        KpiComparator._style_axes(
            axes,
            rotate_x_labels=30,
            fontsize=12,
            common_legends=True,
            suptitle=title,
            leg_base_height=1.1,
        )
        axes[0].set_ylabel("# Trips / person / day")

        return fig

    def plot_calibration_for_mode_share(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("calibration_mode_share", **kwargs)
        df.simulated *= 100
        df.target *= 100

        if df is None or df.empty:
            logging.warning("There were no results for calibrating mode share")
            return

        fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(20, 8), sharey="col")

        self._overlay_barplots(df[df["type"] == "HBW"], "mode", axes[0], "Home-Based Work")
        self._overlay_barplots(df[df["type"] == "HBO"], "mode", axes[1], "Home-Based Other")
        self._overlay_barplots(df[df["type"] == "NHB"], "mode", axes[2], "Non Home-Based")
        self._overlay_barplots(df[df["type"] == "TOTAL"], "mode", axes[3], "Total")

        [axes[i].legend().remove() for i in [0, 1, 2]]  # Just leave the legend in the final (total) plot

        KpiComparator._style_axes(axes, rotate_x_labels=50, suptitle="Mode Share Validation")
        axes[0].set_ylabel("Proportion of Trips (%)")

        return fig

    def plot_calibration_for_boardings(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("calibration_boardings", **kwargs)
        if df is None or df.empty:
            logging.warning("There were no results for calibrating boardings")
            return

        df_agency = df.groupby(["run_id", "agency"]).agg({"simulated": "sum", "target": "sum"}).reset_index()
        df_mode = df.groupby(["run_id", "mode"]).agg({"simulated": "sum", "target": "sum"}).reset_index()

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
        self._overlay_barplots(df_agency, "agency", ax[0], "By Agency")
        self._overlay_barplots(df_mode, "mode", ax[1], "By Mode")

        KpiComparator._style_axes(ax, rotate_x_labels=50, suptitle="PT Boardings Validation", common_legends=True)
        fig.subplots_adjust(top=0.90)

        return fig

    def plot_validation_for_speeds(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("validation_speed", **kwargs)
        if df is None or df.empty:
            logging.warning("There were no results for validating speeds")
            return

        fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(20, 8), sharex="all")

        def f(time_period, ax, title):
            self._overlay_barplots(df[df["time_period"] == time_period], "link_type", ax, title)

        f("AM", ax[0], "AM-Peak Speeds (in mi/hr)")
        f("PM", ax[1], "PM-Peak Speeds (in mi/hr)")
        f("OP", ax[2], "Off-Peak Speeds (in mi/hr)")

        return fig

    def plot_calibration_timing(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("calibration_timing", **kwargs)

        if df is None or df.empty:
            logging.warning("There were no results for calibrating timing choice")
            return

        def f(act_type, ax, title):
            self._overlay_barplots(df[df["act_type"] == act_type], "period", ax, title)

        df.simulated *= 100
        df.target *= 100

        activities = df["act_type"].unique()
        activities = activities[activities != "TOTAL"]
        activities = np.append(activities, "TOTAL")

        df.period = df.period.map(
            {
                "NIGHT": "0-6",
                "AMPEAK": "6-9",
                "AMOFFPEAK": "9-12",
                "PMOFFPEAK": "12-16",
                "PMPEAK": "16-19",
                "EVENING": "19-24",
            }
        )
        df = df.sort_values("period")

        ncols = 6
        nrows = len(activities) // ncols + 1
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(20, 8), sharey="all", sharex="all")
        axes = axes.reshape(-1)
        for i, act_type in enumerate(activities):
            f(act_type, axes[i], act_type)
            axes[i].set_ylim(0, 100)
            axes[i].set_ylabel("% of Activities")
            if act_type.lower() != "total":
                axes[i].legend().remove()
            for side in ["top", "left", "right"]:
                axes[i].spines[side].set_visible(False)
                axes[i].tick_params(axis="y", which="major", length=0)

        KpiComparator._style_axes(axes, rotate_x_labels=50, fontsize=10)
        plt.suptitle("Timing Choice Validation", fontsize=20)
        for j in range(i + 1, nrows * ncols):
            axes[j].set_frame_on(False)
            axes[j].grid(False)
            axes[j].tick_params(axis="y", which="major", length=0)

        fig.subplots_adjust(hspace=0.3)
        return fig

    def plot_calibration_destination(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("calibration_destination", **kwargs)

        if df is None or df.empty:
            logging.warning("There were no results for calibrating destination choice")
            return

        if "data_type" not in df:
            logging.warning("deprecation warning: plotting destination choice calibration missing 'data_type' column")
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 8), sharex="all")
            self._overlay_barplots(df, "acttype", ax, None)  # "Trip Distance")
            ax = [ax]
            ax[0].set_ylabel("Distance (km)")
        else:
            fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(20, 8), sharex="all")
            self._overlay_barplots(df[(df["data_type"] == "distance")], "acttype", ax[0], None)  # "Trip Distance")
            self._overlay_barplots(
                df[(df["data_type"] == "travel_time")], "acttype", ax[1], None
            )  # "Trip Travel Time")
            ax[0].set_ylabel("Distance (km)")
            ax[1].set_ylabel("Time (minutes)")

        KpiComparator._style_axes(
            ax, rotate_x_labels=30, common_legends=True, suptitle="Destination Choice Validation", leg_base_height=1.1
        )

        return fig

    def plot_count_validation(self, **kwargs):
        import matplotlib.pyplot as plt

        df = self._get_results("count_validation", **kwargs).dropna()

        types, type_str = filter_list_for_display(kwargs.get("types", "All"), df["type"].unique())
        df = df[df["type"].isin(types)]

        period = kwargs.get("period", "Daily")
        df = df[df.period == period]

        x, y = df.observed_volume, df.simulated_volume

        fig, ax = plt.subplots(1, 1)
        scatter_plot(x, y, ax, f"{type_str} Link Count Validation ({period})")

        return fig

    def _get_results(self, result_name, **kwargs):
        """Collates together dataframes from each run and annotates them appropriately."""
        if "df" in kwargs:
            # Allow a user to pass in a pre-existing data frame
            df = kwargs["df"].copy()
        else:
            run_ids = self._limit_run_ids(**kwargs)
            skip_cache = kwargs.get("skip_cache", False)
            force_cache = kwargs.get("force_cache", False)
            dfs = [
                self._maybe_metric(result_name, kpi, run_id, skip_cache=skip_cache, force_cache=force_cache)
                for run_id, kpi in self.runs.items()
                if run_id in run_ids
            ]
            dfs = [df for df in dfs if df is not None and not df.empty]
            if not dfs:
                return None
            df = pd.concat(dfs)

        if kwargs.get("df_transform", None) is not None:
            df = kwargs["df_transform"](df)
        if kwargs.get("df_filter", None) is not None:
            df = filter_df(df, kwargs["df_filter"])
        if (sort_key := kwargs.get("sort_key", None)) is not None:
            if callable(sort_key):
                df = df.sort_values(by="run_id", key=sort_key)
            else:
                df = df.sort_values(by=sort_key)
        else:
            df = df.sort_values(by="run_id")
        return df

    def _limit_run_ids(self, **kwargs):
        limit_runs = kwargs.get("limit_runs", None)
        if limit_runs is None:
            return set(self.runs.keys())

        # limit runs
        if isinstance(limit_runs, int):
            # limit_runs is a number of runs to show (either first N if N>0, or last N otherwise)
            run_ids = list(self.runs.keys())
            return set(run_ids[-limit_runs:]) if limit_runs > 0 else set(run_ids[:-limit_runs])
        elif isinstance(limit_runs, Pattern):
            return {r for r in self.runs.keys() if limit_runs.match(r)}
        else:
            return {r for r in self.runs.keys() if limit_runs(r)}
        return set(limit_runs)

    def _maybe_metric(self, metric, kpi, run_id, skip_cache, force_cache):
        try:
            return self._add_run_attributes(
                kpi.get_cached_kpi_value(metric, skip_cache=skip_cache, force_cache=force_cache), run_id
            )
        except Exception:
            tb = traceback.format_exc()
            logging.info(f"Exception while getting {metric} for {run_id}")
            logging.info(tb)
            return None
        finally:
            kpi.close()

    def _add_run_attributes(self, df, run_id):
        return df if df is None or not isinstance(df, pd.DataFrame) else df.assign(run_id=run_id)
