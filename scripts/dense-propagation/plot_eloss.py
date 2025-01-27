# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import uproot
import awkward as ak
import numpy as np
import pandas as pd
import scipy.stats


def stat_mean(data):
    m = np.mean(data)
    return m


def stat_std(data):
    s = np.std(data)
    return s


def fit_landau(data):
    loc, scale = scipy.stats.moyal.fit(data, method="mle")
    return loc, scale


def stat_mode_landau(data):
    loc, scale = fit_landau(data)
    return loc


def stat_mean_landau(data):
    loc, scale = fit_landau(data)
    mean = scipy.stats.moyal.stats(loc, scale, moments="m")
    return mean


def stat_std_landau(data):
    loc, scale = fit_landau(data)
    var = scipy.stats.moyal.stats(loc, scale, moments="v")
    return np.sqrt(var)


def fwhm_landau(loc, scale):
    pdf_max = scipy.stats.moyal.pdf(loc, loc, scale)
    left_space = np.linspace(0, loc, 10000)
    left = left_space[
        np.argmax(scipy.stats.moyal.pdf(left_space, loc, scale) > pdf_max / 2)
    ]
    right_space = np.linspace(loc, 4 * loc, 10000)
    right = right_space[
        np.argmax(scipy.stats.moyal.pdf(right_space, loc, scale) < pdf_max / 2)
    ]
    return left, right


def fwhm_to_std(fwhm):
    return fwhm * 0.42466090014400953


def stat_fwhm_landau(data):
    loc, scale = fit_landau(data)
    left, right = fwhm_landau(loc, scale)
    return right - left


def stat_fwhm_std_landau(data):
    loc, scale = fit_landau(data)
    left, right = fwhm_landau(loc, scale)
    fwhm = abs(right - left)
    return fwhm_to_std(fwhm)


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "--g4-input",
    type=Path,
    default=f"{base_dir}/data/dense-propagation/geant4/logscale_mom_fe.root",
    help="Path to Geant4 input file",
)
parser.add_argument(
    "--acts-input",
    type=Path,
    default=f"{base_dir}/data/dense-propagation/acts/eloss_fe.csv",
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
args = parser.parse_args()

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_title("Energy loss of muons in 100 mm Fe")
ax.set_xlabel("Initial momentum [GeV]")
ax.set_ylabel("Energy loss [GeV/mm]")

log_range = (np.log10(args.e_range[0]), np.log10(args.e_range[1]))
edges = 10 ** np.linspace(log_range[0], log_range[1], args.bins)
mid = 0.5 * (edges[:-1] + edges[1:])

if args.g4_input is not None:
    g4_data = ak.to_dataframe(
        uproot.open(args.g4_input)["reading"].arrays(library="ak")
    )

    g4_e_init = g4_data["e_init"]
    g4_e_final = g4_data["e_final"]
    g4_e_loss = g4_data["e_loss"]

    # thickness in mm
    g4_e_loss = g4_e_loss / 100

    for p_min, p_max in [
        # (290, 310),
        # (0.9, 1.1),
    ]:
        ofig, oax = plt.subplots(1, 1, figsize=(4, 3))
        oax.set_xscale("log")
        oax.set_yscale("log")
        mask = (g4_e_init > p_min) & (g4_e_init < p_max)
        oax.hist(
            g4_e_loss[mask],
            bins=10000,
            density=True,
            histtype="step",
            color="deepskyblue",
            label="Geant4",
        )
        loc, scale = fit_landau(g4_e_loss[mask])
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
        acts_mask = (acts_eloss["p_initial"] > p_min) & (acts_eloss["p_initial"] < p_max)
        acts_mean = acts_eloss["bethe"][acts_mask].mean()
        acts_mode = 0.9 * acts_mean
        acts_std = acts_eloss["landau_sigma"][acts_mask].mean()

        if False:
            oax.axvline(acts_mean, color="red", linestyle="--", label="ACTS mean")
            oax.axvline(
                acts_mean - acts_std,
                color="orange",
                linestyle="--",
                label="ACTS mean - std",
            )
            oax.axvline(
                acts_mean + acts_std,
                color="orange",
                linestyle="--",
                label="ACTS mean + std",
            )

            oax.axvline(acts_mode, color="green", linestyle="--", label="ACTS mode")
            oax.axvline(
                acts_mode - acts_std,
                color="limegreen",
                linestyle="--",
                label="ACTS mode - std",
            )
            oax.axvline(
                acts_mode + acts_std,
                color="limegreen",
                linestyle="--",
                label="ACTS mode + std",
            )

        oax.legend()

    g4_mean, _, _ = scipy.stats.binned_statistic(
        g4_e_init,
        g4_e_loss,
        bins=edges,
        range=log_range,
        statistic=stat_mean_landau,
    )
    g4_std, _, _ = scipy.stats.binned_statistic(
        g4_e_init,
        g4_e_loss,
        bins=edges,
        range=log_range,
        statistic=stat_fwhm_std_landau,
    )

    # ax.hist(e_init, bins=edges, range=log_range, histtype="step")

    ax.errorbar(mid, g4_mean, yerr=g4_std, fmt="o", linestyle="", label="Geant4")
    # ax.plot(mid, g4_mean, marker="o", linestyle="", label="Geant4")

if args.acts_input is not None:
    acts_eloss = pd.read_csv(args.acts_input)

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
        label="ACTS",
    )
    # ax.plot(mid, acts_total_mean, marker="^", linestyle="", label="ACTS")
    # ax.plot(mid, acts_bethe, label="ACTS bethe")

ax.set_xscale("log")
ax.set_yscale("log")

ax.legend()

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
