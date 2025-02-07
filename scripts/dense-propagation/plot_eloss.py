# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats

from common import read_g4_data, make_g4_eloss_stats, read_acts_data, stat_mean
from common import fit_landau, fwhm_landau, fwhm_to_std


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "--g4-input",
    type=Path,
    default=f"{base_dir}/data/dense-propagation/geant4/logscale_mom_fe_1000mm.root",
    help="Path to Geant4 input file",
)
parser.add_argument(
    "--acts-input",
    type=Path,
    default=f"{base_dir}/data/dense-propagation/acts/msc_eloss_fe_1000mm.csv",
    help="Path to ACTS input file",
)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/dense-propagation/eloss_cmp.pdf",
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
parser.add_argument("--bins", type=int, default=30, help="Number of bins")
parser.add_argument(
    "--e-range", nargs=2, default=[0.05, 300], help="Energy range in GeV"
)
parser.add_argument("--min-p-out", type=float, default=0, help="Minimum output momentum")
args = parser.parse_args()

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_title("Energy loss of muons in 100 mm Fe")
ax.set_xlabel("Initial momentum [GeV]")
ax.set_ylabel("Energy loss [GeV/mm]")

log_range = (np.log10(args.e_range[0]), np.log10(args.e_range[1]))
edges = 10 ** np.linspace(log_range[0], log_range[1], args.bins)
mid = 0.5 * (edges[:-1] + edges[1:])

if args.g4_input is not None:
    g4_data = read_g4_data(args.g4_input, args.min_p_out)
    g4_mode, g4_mean, g4_std = make_g4_eloss_stats(g4_data, edges, log_range)

    ax.errorbar(mid, g4_mean, yerr=g4_std, fmt="o", linestyle="", label="Geant4")

if args.acts_input is not None:
    acts_data = read_acts_data(args.acts_input, args.min_p_out)

    acts_total_mean, _, _ = scipy.stats.binned_statistic(
        acts_data["p_initial"],
        acts_data["e_loss"],
        bins=edges,
        range=log_range,
        statistic=stat_mean,
    )

    acts_std, _, _ = scipy.stats.binned_statistic(
        acts_data["p_initial"],
        acts_data["e_sigma"],
        bins=edges,
        range=log_range,
        statistic=stat_mean,
    )

    ax.errorbar(mid, acts_total_mean, yerr=acts_std, marker="^", linestyle="", label="ACTS")

ax.set_xscale("log")
ax.set_yscale("log")

ax.legend()

for p_min, p_max in [
    #(290, 310),
    #(0.9, 1.1),
]:
    ofig, oax = plt.subplots(1, 1, figsize=(4, 3))
    oax.set_title(f"{p_min} {p_max}")
    oax.set_xscale("log")
    oax.set_yscale("log")
    mask = (g4_data["p_initial"] > p_min) & (g4_data["p_initial"] < p_max)
    oax.hist(
        g4_data["e_loss"][mask],
        bins=10000,
        density=True,
        histtype="step",
        color="deepskyblue",
        label="Geant4",
    )
    loc, scale = fit_landau(g4_data["e_loss"][mask])
    left, right = fwhm_landau(loc, scale)
    mean = stat_mean(g4_data["e_loss"][mask])
    std = fwhm_to_std(right - left)

    if True:
        oax.axvline(loc, color="deepskyblue", linestyle="--", label="Landau mode")
        oax.axvline(mean, color="deepskyblue", linestyle="--", label="Landau mean")
        oax.axvline(left, color="skyblue", linestyle="--", label="FWHM")
        oax.axvline(right, color="skyblue", linestyle="--", label="FWHM")
        oax.axvline(
            loc - std,
            color="lightskyblue",
            linestyle="--",
            label="Landau mode - std",
        )
        oax.axvline(
            loc + std,
            color="lightskyblue",
            linestyle="--",
            label="Landau mode + std",
        )

    if True:
        g4_fit_x = np.linspace(0.01 * loc, 10 * loc, 1000)
        g4_fit_y = scipy.stats.landau.pdf(g4_fit_x, loc, scale)
        oax.plot(
            g4_fit_x,
            g4_fit_y,
            color="deepskyblue",
            linestyle="--",
            label="Landau fit",
        )

    acts_mask = (acts_data["p_initial"] > p_min) & (acts_data["p_initial"] < p_max)
    acts_mean = acts_data[acts_mask]["e_loss"].mean()

    print("acts", acts_mean, acts_data[acts_mask]["e_sigma"].mean())
    print("g4", mean, std)

    if True:
        oax.axvline(acts_mean, color="red", linestyle="--", label="ACTS mean")
        # oax.axvline(
        #     acts_mean - acts_std,
        #     color="orange",
        #     linestyle="--",
        #     label="ACTS mean - std",
        # )
        # oax.axvline(
        #     acts_mean + acts_std,
        #     color="orange",
        #     linestyle="--",
        #     label="ACTS mean + std",
        # )

    oax.legend()

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
