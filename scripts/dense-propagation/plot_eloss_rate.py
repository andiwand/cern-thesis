# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import atlasify

from common import (
    material_label,
    read_g4_data,
    read_acts_data,
    make_g4_eloss_stats,
    fit_landau,
    fwhm_landau,
    fwhm_to_std,
    stat_mean,
)


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "material",
    type=str,
    choices=["fe", "lar"],
)
parser.add_argument(
    "thickness",
    type=int,
    help="Thickness in mm",
)
parser.add_argument(
    "--g4-input",
    type=Path,
    help="Path to Geant4 input file",
)
parser.add_argument(
    "--acts-input",
    type=Path,
    help="Path to Acts input file",
)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
parser.add_argument("--bins", type=int, default=30, help="Number of bins")
parser.add_argument(
    "--e-range", nargs=2, default=[0.05, 300], help="Energy range in GeV"
)
parser.add_argument(
    "--min-p-out", type=float, default=0, help="Minimum output momentum"
)
args = parser.parse_args()

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

# ax.set_title("Energy loss of muons in 100 mm Fe")
ax.set_xlabel("Initial momentum [GeV]")
ax.set_ylabel("Energy loss [GeV/mm]")

ax.set_xscale("log")
ax.set_yscale("log")

log_range = (np.log10(args.e_range[0]), np.log10(args.e_range[1]))
edges = 10 ** np.linspace(log_range[0], log_range[1], args.bins)
mid = 0.5 * (edges[:-1] + edges[1:])

if args.g4_input is not None:
    g4_data = read_g4_data(args.g4_input, args.min_p_out)

    # thickness in mm
    thickness = float(re.search(r"_(\d+)mm", args.g4_input.stem).group(1))
    g4_data["e_loss"] = g4_data["e_loss"] / thickness

    for p_min, p_max in [
        # (290, 310),
        # (0.9, 1.1),
    ]:
        ofig, oax = plt.subplots(1, 1, figsize=(4, 3))
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
        std = fwhm_to_std(right - left)

        if False:
            oax.axvline(loc, color="deepskyblue", linestyle="--", label="Landau mode")
            oax.axvline(left, color="skyblue", linestyle="--", label="FWHM")
            oax.axvline(right, color="skyblue", linestyle="--")
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

        if False:
            g4_fit_x = np.linspace(0.01 * loc, 10 * loc, 1000)
            g4_fit_y = scipy.stats.moyal.pdf(g4_fit_x, loc, scale)
            oax.plot(
                g4_fit_x,
                g4_fit_y,
                color="deepskyblue",
                linestyle="--",
                label="Landau fit",
            )

        acts_eloss = pd.read_csv(f"{base_dir}/data/dense-propagation/acts/eloss_fe.csv")
        acts_mask = (acts_eloss["p_initial"] > p_min) & (
            acts_eloss["p_initial"] < p_max
        )
        acts_mean = acts_eloss["bethe"][acts_mask].mean()
        acts_mode = 0.9 * acts_mean
        acts_std = acts_eloss["landau_sigma"][acts_mask].mean()

        if False:
            oax.axvline(acts_mean, color="red", linestyle="--", label="Acts mean")
            oax.axvline(
                acts_mean - acts_std,
                color="orange",
                linestyle="--",
                label="Acts mean - std",
            )
            oax.axvline(
                acts_mean + acts_std,
                color="orange",
                linestyle="--",
                label="Acts mean + std",
            )

            oax.axvline(acts_mode, color="green", linestyle="--", label="Acts mode")
            oax.axvline(
                acts_mode - acts_std,
                color="limegreen",
                linestyle="--",
                label="Acts mode - std",
            )
            oax.axvline(
                acts_mode + acts_std,
                color="limegreen",
                linestyle="--",
                label="Acts mode + std",
            )

        oax.legend()

    g4_mode, g4_mean, g4_std = make_g4_eloss_stats(g4_data, edges, log_range)

    # ax.hist(e_init, bins=edges, range=log_range, histtype="step")

    ax.errorbar(mid, g4_mean, yerr=g4_std, fmt="o", linestyle="", label="Geant4")
    # ax.plot(mid, g4_mean, marker="o", linestyle="", label="Geant4")

if args.acts_input is not None:
    acts_eloss = read_acts_data(args.acts_input)

    acts_total_mean, _, _ = scipy.stats.binned_statistic(
        acts_eloss["p_initial"],
        acts_eloss["total_mean"],
        bins=edges,
        range=log_range,
        statistic=stat_mean,
    )
    acts_bethe_mean, _, _ = scipy.stats.binned_statistic(
        acts_eloss["p_initial"],
        acts_eloss["bethe"],
        bins=edges,
        range=log_range,
        statistic=stat_mean,
    )
    acts_landau_sigma, _, _ = scipy.stats.binned_statistic(
        acts_eloss["p_initial"],
        acts_eloss["landau_sigma"],
        bins=edges,
        range=log_range,
        statistic=stat_mean,
    )

    ax.errorbar(
        mid,
        acts_total_mean,
        yerr=acts_landau_sigma,
        fmt="^",
        linestyle="",
        label="Acts",
    )
    # ax.plot(mid, acts_total_mean, marker="^", linestyle="", label="Acts")
    # ax.plot(mid, acts_bethe, label="Acts bethe")

ax.legend()

atlasify.atlasify(
    axes=ax,
    brand="Acts",
    atlas="Simulation",
    subtext=f"Acts v40.0.0\nsingle muons in {args.thickness} mm of {material_label(args.material)}",
)

ylim = ax.get_ylim()
ax.set_ylim(ylim[0], ylim[1] * 1.5)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
