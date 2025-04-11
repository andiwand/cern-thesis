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
from mycommon2.stats import clopper_pearson


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("mu_particles_selected", type=Path)
parser.add_argument("pi_particles_selected", type=Path)
parser.add_argument("e_particles_selected", type=Path)
parser.add_argument("mu_particles", type=Path)
parser.add_argument("pi_particles", type=Path)
parser.add_argument("e_particles", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

ptypes = ["mu", "pi", "e"]

particles_selected = [args.mu_particles_selected, args.pi_particles_selected, args.e_particles_selected]
particles_selected = [uproot.open(p) for p in particles_selected]
particles_selected = [ak.to_dataframe(p["particles"].arrays(["m", "q", "p", "pt", "phi", "eta"], library="ak"), how="outer").dropna() for p in particles_selected]
particles = [args.mu_particles, args.pi_particles, args.e_particles]
particles = [uproot.open(p) for p in particles]
particles = [ak.to_dataframe(p["particles"].arrays(["m", "q", "p", "pt", "phi", "eta"], library="ak"), how="outer").dropna() for p in particles]

eta_bins = 30
eta_edges = np.linspace(-3, 3, eta_bins + 1)
eta_centers = (eta_edges[:-1] + eta_edges[1:]) / 2

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Detector efficiency")

ax.set_xlim(-3, 3)

ax.hlines(1, -3, 3, linestyles="--", color="gray")

for i, ptype, p_selected, p_all in zip(range(3), ptypes, particles_selected, particles):
    count_selected_over_eta, _, _ = binned_statistic(
        p_selected["eta"],
        np.ones(len(p_selected)),
        statistic="sum",
        bins=eta_edges,
    )
    count_total_over_eta, _, _ = binned_statistic(
        p_all["eta"],
        np.ones(len(p_all)),
        statistic="sum",
        bins=eta_edges,
    )

    ys, yerr_upper, yerr_lower = clopper_pearson(
        count_selected_over_eta,
        count_total_over_eta,
    )

    ax.errorbar(
        eta_centers,
        ys,
        yerr=(ys - yerr_lower, yerr_upper - ys),
        xerr=(eta_edges[1:] - eta_edges[:-1]) / 2,
        label=f"{ptype}",
        marker=get_marker(i),
        linestyle="",
        color=get_color(i),
    )

ax.legend()

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0\nsingle particles, <$\\mu$> = 0, $p_T$ = 10 GeV",
)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
