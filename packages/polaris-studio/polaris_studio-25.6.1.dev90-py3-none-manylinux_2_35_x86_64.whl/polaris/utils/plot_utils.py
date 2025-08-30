# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import warnings
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import linregress  # type: ignore
from collections.abc import Iterable


def get_scatter_stats(x, y, intercept=True):
    x = np.array(x)
    y = np.array(y)
    stats = {
        "Count": len(x),
        "Mean(x)": np.mean(x),
        "Mean(y)": np.mean(y),
        "% Diff": np.mean(y - x) / np.mean(x),
        "% RMSE": np.sqrt(np.mean(np.square(y - x))) / np.mean(x),
    }
    try:
        if intercept:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                reg = linregress(x, y)
                stats["slope"] = reg.slope
                stats["intercept"] = reg.intercept
                stats["R^2"] = pow(reg.rvalue, 2)
        else:
            stats = stats | fit_fixed_intercept(x, y, intercept=0)
    except Exception:
        reg = None
        stats["slope"] = None
        stats["intercept"] = None
        stats["R^2"] = None

    return stats


def fit_fixed_intercept(x, y, intercept=0):
    x = np.asarray(x)
    y = np.asarray(y)
    y_adj = y - intercept
    slope = np.dot(x, y_adj) / np.dot(x, x)

    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)

    return {"slope": slope, "intercept": intercept, "R^2": 1 - ss_res / ss_tot}


def scatter_plot(x, y, ax=None, title=None, xlabel="Observed", ylabel="Simulated", intercept=True, mpe=True):
    if ax is None:
        _, ax = plt.subplots(1, 1)
    ax.scatter(x, y, color="dodgerblue", edgecolors="skyblue", s=25, zorder=10, alpha=0.5)
    stats = get_scatter_stats(x, y, intercept)
    intercept_str = f"{stats['intercept']:+.1f}" if intercept else ""
    stat_str = f"$y \\approx {stats['slope']:.2f}x {intercept_str}$\n"
    stat_str += f"$R^2={stats['R^2']:.3f}$\n"
    stat_str += rf"MPE$ = {stats['% Diff']*100:+.1f}\%$" if mpe else ""
    ax.text(
        0.03,
        0.97,
        stat_str,
        fontsize=10,
        horizontalalignment="left",
        verticalalignment="top",
        transform=ax.transAxes,
    )
    ax_limits = (min(x.min(), y.min()) * 0.9, max(x.max(), y.max()) * 1.03)
    ax.set_xlim(ax_limits)
    ax.set_ylim(ax_limits)
    ax.axline(xy1=(0, 0), slope=1, c="grey", linestyle="dotted", linewidth=0.5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if stats["slope"] and stats["intercept"]:
        ax.axline(xy1=(0, stats["intercept"]), slope=stats["slope"])
    if title is not None:
        ax.get_figure().suptitle(title)


def is_non_string_iterable(x):
    return isinstance(x, Iterable) and not isinstance(x, str)


def filter_list_for_display(filter_to, list):
    """Filter the given list based on arg:
      if `arg.upper()` is "ALL", then `list` is returned.
    If `arg` is a scalar that is not "All", then `[arg]` is returned.
    Otherwise, `arg` is returned."""

    if is_non_string_iterable(filter_to):
        return filter_to, ", ".join([str(s) for s in filter_to])
    if isinstance(filter_to, str) and filter_to.upper() == "ALL":
        return list, "All"
    return [filter_to], str(filter_to)


def extract_common_legend(
    axes,
    ncol=4,
    legend_loc="lower center",
    legend_anchor=None,
    leg_base_height=0.7,
):
    legend_elements = axes[0].get_legend_handles_labels()
    fig = axes[0].figure
    legend = fig.legend(
        *legend_elements,
        loc=legend_loc,
        ncol=ncol,
        fontsize=12,
        bbox_to_anchor=legend_anchor,
    )
    num_legend_elements = len(np.ravel(legend_elements)) / 2
    num_legend_rows = int(float(num_legend_elements) / ncol) + int(num_legend_elements % ncol > 0)
    if num_legend_elements > 1:
        width, height = fig.get_size_inches()
        height += (num_legend_rows - 1) * 0.4  # 0.4' per extra legend row
        fig.set_size_inches(width, height)
        leg_height = leg_base_height + num_legend_rows * 0.30
        # print(
        #     width,
        #     height,
        #     num_legend_rows,
        #     num_legend_elements,
        #     leg_height,
        #     leg_height / height,
        #     1.0 - 0.5 / height,
        # )
        fig.subplots_adjust(bottom=leg_height / height, top=1.0 - 0.5 / height)

    [ax.legend().remove() for ax in axes]

    return legend
