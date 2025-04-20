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


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("particles", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

particles = uproot.open(args.particles)
particles = ak.to_dataframe(particles["particles"].arrays(["vertex_primary", "vertex_secondary", "particle", "generation", "sub_particle", "phi", "eta", "number_of_hits"], library="ak"), how="outer").dropna()
particles = particles[
    (particles["vertex_primary"] == 1) &
    (particles["vertex_secondary"] == 0) &
    (particles["particle"] == 1) &
    (particles["generation"] == 0) &
    (particles["sub_particle"] == 0)
]

eta_bins = 30
eta_edges = np.linspace(-3, 3, eta_bins + 1)
eta_centers = (eta_edges[:-1] + eta_edges[1:]) / 2

fig, ax = plt.subplots(1, 1, figsize=(8, 4), layout="compressed")

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Number of hits")

ax.set_xlim(-3, 3)

mean_hits_eta, _, _ = binned_statistic(
    particles["eta"],
    particles["number_of_hits"],
    statistic="mean",
    bins=eta_edges,
)
std_hits_eta, _, _ = binned_statistic(
    particles["eta"],
    particles["number_of_hits"],
    statistic="std",
    bins=eta_edges,
)
min_hits_eta, _, _ = binned_statistic(
    particles["eta"],
    particles["number_of_hits"],
    statistic="min",
    bins=eta_edges,
)
max_hits_eta, _, _ = binned_statistic(
    particles["eta"],
    particles["number_of_hits"],
    statistic="max",
    bins=eta_edges,
)
max_hits_eta += 1

counts, xedges, yedges, im = ax.hist2d(
    particles["eta"],
    particles["number_of_hits"],
    bins=(eta_edges, 20),
    range=((-3, 3), (6, 26)),
    cmap="Blues",
    cmin=1,
)

ax.errorbar(
    eta_centers,
    mean_hits_eta,
    yerr=std_hits_eta,
    xerr=(eta_edges[1:] - eta_edges[:-1]) / 2,
    label="mean",
    marker=get_marker(1),
    linestyle="",
    color=get_color(1),
)

ax.step(
    eta_edges,
    list(min_hits_eta) + [min_hits_eta[-1]],
    where="post",
    label="min / max",
    linestyle="--",
    color="grey"
)
ax.step(
    eta_edges,
    list(max_hits_eta) + [max_hits_eta[-1]],
    where="post",
    #label="min",
    linestyle="--",
    color="grey"
)

ax.legend()
cbar = fig.colorbar(im, ax=ax)
cbar.set_ticks([])
cbar.set_label("Density [a.u.]")

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0\nsingle muons, $p_T$ = 100 GeV, <$\\mu$> = 0",
    enlarge=1.2,
)

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
