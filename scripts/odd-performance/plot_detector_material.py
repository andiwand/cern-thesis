#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import uproot
import awkward as ak
import numpy as np
from scipy.stats import binned_statistic
import atlasify

from mycommon1.plots import get_color, get_marker
from mycommon1.stats import ratio_std


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("acts_scan", type=Path)
parser.add_argument("geant4_scan", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

columns = ["event_id", "v_phi", "v_eta", "t_X0", "t_L0", "mat_x", "mat_y", "mat_z", "mat_r", "mat_step_length", "mat_X0", "mat_L0"]

acts_scan = uproot.open(args.acts_scan)
acts_scan = ak.to_dataframe(
    acts_scan["material-tracks"].arrays(columns, library="ak"),
    how="outer",
).dropna()
geant4_scan = uproot.open(args.geant4_scan)
geant4_scan = ak.to_dataframe(
    geant4_scan["material-tracks"].arrays(columns, library="ak"),
    how="outer",
).dropna()

bins = 100
bin_edges = np.linspace(-3, 3, bins + 1)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

fig, axs = plt.subplots(2, 1, figsize=(8, 4), sharex=True, gridspec_kw={"height_ratios": [4, 1]})

#axs[0].set_xlabel(r"$\eta$")
axs[0].set_ylabel("$X/X_0$")

axs[0].set_xlim(-3, 3)

data = []
for i, scan, label in zip(
    range(2),
    [geant4_scan, acts_scan],
    ["Geant4", "Acts"],
):
    scan["mat_step_X0"] = scan["mat_step_length"] / scan["mat_X0"]
    scan["mat_step_L0"] = scan["mat_step_length"] / scan["mat_L0"]
    scan = scan[(scan["mat_z"].abs() < 3200) & (scan["mat_r"] < 1120)]

    scan = scan.groupby("event_id").agg(
        {
            "v_phi": "first",
            "v_eta": "first",
            "t_X0": "first",
            "t_L0": "first",
            "mat_step_length": "sum",
            "mat_step_X0": "sum",
            "mat_step_L0": "sum",
        }
    )

    bin_means, _, _ = binned_statistic(
        scan["v_eta"], scan["mat_step_X0"], statistic="mean", bins=bin_edges
    )
    bin_stds, _, _ = binned_statistic(
        scan["v_eta"], scan["mat_step_L0"], statistic="std", bins=bin_edges
    )

    axs[0].errorbar(
        bin_centers,
        bin_means,
        yerr=bin_stds,
        xerr=(bin_edges[1:] - bin_edges[:-1]) / 2,
        label=label,
        marker=get_marker(i),
        linestyle="",
        color=get_color(i),
        alpha=0.5,
    )

    data.append((bin_means, bin_stds))

axs[0].legend(loc="upper right")

atlasify.atlasify(
    axes=axs[0],
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0\n",
)

ylim = axs[0].get_ylim()
axs[0].set_ylim(0, ylim[1])

# ratio plot
axs[1].set_xlabel(r"$\eta$")
axs[1].set_ylabel("Ratio")

axs[1].errorbar(
    bin_centers,
    np.ones(len(bin_centers)),
    xerr=(bin_edges[1:] - bin_edges[:-1]) / 2,
    #label="Geant4",
    marker=get_marker(0),
    linestyle="",
    color=get_color(0),
    alpha=0.5,
)

axs[1].errorbar(
    bin_centers,
    data[1][0] / data[0][0],
    yerr=ratio_std(data[1][0], data[0][0], data[1][1], data[0][1]),
    xerr=(bin_edges[1:] - bin_edges[:-1]) / 2,
    #label="Acts",
    marker=get_marker(1),
    linestyle="",
    color=get_color(1),
    alpha=0.5,
)

atlasify.atlasify(
    axes=axs[1],
    brand=None,
    atlas=None,
    subtext=None,
)

ylim = 0.2
axs[1].set_ylim(1 - ylim, 1 + ylim)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
