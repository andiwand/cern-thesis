#!/usr/bin/env python3

import argparse
from pathlib import Path
import numpy as np
import uproot
import awkward as ak
import scipy.stats
import matplotlib.pyplot as plt

from mycommon.stats import robust_gauss_fit


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("vertex_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

variables = [
    "resX",
    "resY",
    "resZ",
    "resT",
]
columns = [
    "vertex_primary",
    "vertex_secondary",
    "nTrueVtx",
] + variables

vertexing = ak.to_dataframe(
    uproot.open(args.vertex_perf)["vertexing"].arrays(columns, library="ak"),
    how="outer",
)

# filter for first primary vertex which is the HS vertex by design
vertexing = vertexing[
    (vertexing["vertex_primary"] == 1) & (vertexing["vertex_secondary"] == 0)
]

fig, axs = plt.subplots(2, 2, figsize=(8, 4))
axs = [item for sublist in axs for item in sublist]

nbins = 30
ylabels = [
    r"residual x [mm]",
    r"residual y [mm]",
    r"residual z [mm]",
    r"residual t [mm]",
]

for i, variable, ax, ylabel in zip(
    range(4),
    variables,
    axs,
    ylabels
):
    data = vertexing[variable].dropna()
    (mu, sigma), cov = robust_gauss_fit(data)

    range = (mu - 5 * sigma, mu + 5 * sigma)

    ax.set_xlabel(ylabel)
    if i == 0 or i == 2:
        ax.set_ylabel("Density")

    n, bins, patches = ax.hist(
        vertexing[variable],
        nbins,
        range=range,
        histtype="step",
        density=True,
    )

    x = np.linspace(range[0], range[1], 100)
    ax.plot(
        x,
        scipy.stats.norm.pdf(x, mu, sigma),
        label=f"mu={mu:.2E}\nsigma={sigma:.2E}",
    )

    ax.vlines(0, 0, ax.get_ylim()[1], color="grey", linestyle="--")

    ax.legend(loc="lower right")

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
