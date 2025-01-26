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


def mean(data):
    m = np.mean(data)
    return m


def std(data):
    s = np.std(data)
    return s


def fit_landau(data):
    loc, scale = scipy.stats.moyal.fit(data)
    return loc, scale


def mode_landau(data):
    loc, scale = fit_landau(data)
    return loc


def mean_landau(data):
    loc, scale = fit_landau(data)
    mean = scipy.stats.moyal.stats(loc, scale, moments="m")
    return mean


def std_landau(data):
    loc, scale = fit_landau(data)
    var = scipy.stats.moyal.stats(loc, scale, moments="v")
    return np.sqrt(var)


def fwhm_landau(loc, scale):
    pdf_max = scipy.stats.moyal.pdf(loc, loc, scale)
    left_space = np.linspace(0, loc, 10000)
    left = left_space[np.argmax(scipy.stats.moyal.pdf(left_space, loc, scale) > pdf_max / 2)]
    right_space = np.linspace(loc, 4 * loc, 10000)
    right = right_space[np.argmax(scipy.stats.moyal.pdf(right_space, loc, scale) < pdf_max / 2)]
    return left, right


def fwhm_to_std(fwhm):
    return fwhm * 0.42466090014400953


def fwhm_std_landau(data):
    loc, scale = fit_landau(data)
    left, right = fwhm_landau(loc, scale)
    fwhm = right - left
    return fwhm_to_std(fwhm)


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("--show", action="store_true", help="Show the plot")
args = parser.parse_args()

data = ak.to_dataframe(
    uproot.open(f"{base_dir}/data/dense-propagation/geant4/chart_eloss_fe.root")["reading"].arrays(library="ak")
)
data = ak.to_dataframe(
    uproot.open(f"chart_eloss.root")["reading"].arrays(library="ak")
)

e_init = data["e_init"]
e_final = data["e_final"]
e_loss = data["e_loss"]

# thickness in mm
e_loss = e_loss / 100

bins = 30
e_range = (0.05, 1000)  # in GeV

if False:
    p_min, p_max = 790, 810

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_yscale("log")
    mask = (e_init > p_min) & (e_init < p_max)
    ax.hist(e_loss[mask], bins=1000, histtype="step", color="deepskyblue", label="Geant4")
    loc, scale = fit_landau(e_loss[mask])
    left, right = fwhm_landau(loc, scale)
    std = fwhm_to_std(right - left)
    ax.axvline(loc, color="deepskyblue", linestyle="--", label="Landau mode")
    ax.axvline(left, color="skyblue", linestyle="--", label="FWHM")
    ax.axvline(right, color="skyblue", linestyle="--")
    ax.axvline(loc - std, color="lightskyblue", linestyle="--", label="Landau mode - std")
    ax.axvline(loc + std, color="lightskyblue", linestyle="--", label="Landau mode + std")

    g4_fit_x = np.linspace(0.9*loc, 2*loc, 1000)
    g4_fit_y = scipy.stats.moyal.pdf(g4_fit_x, loc, scale) * np.sum(mask)
    ax.plot(g4_fit_x, g4_fit_y, color="deepskyblue", linestyle="--", label="Landau fit")

    acts_eloss = pd.read_csv(f"{base_dir}/data/dense-propagation/acts/eloss_fe.csv")
    acts_mask = (acts_eloss["p"] > p_min) & (acts_eloss["p"] < p_max)
    acts_mean = acts_eloss["bethe"][acts_mask].mean()
    acts_mode = 0.9 * acts_mean
    acts_std = acts_eloss["landau_sigma"][acts_mask].mean()

    ax.axvline(acts_mean, color="red", linestyle="--", label="ACTS mean")
    ax.axvline(acts_mean - acts_std, color="orange", linestyle="--", label="ACTS mean - std")
    ax.axvline(acts_mean + acts_std, color="orange", linestyle="--", label="ACTS mean + std")

    ax.axvline(acts_mode, color="green", linestyle="--", label="ACTS mode")
    ax.axvline(acts_mode - acts_std, color="limegreen", linestyle="--", label="ACTS mode - std")
    ax.axvline(acts_mode + acts_std, color="limegreen", linestyle="--", label="ACTS mode + std")

    ax.legend()

fig, ax = plt.subplots(1, 1, figsize=(12, 8))

log_range = (np.log10(e_range[0]), np.log10(e_range[1]))
edges = 10 ** np.linspace(log_range[0], log_range[1], bins)
g4_mean, _, _ = scipy.stats.binned_statistic(
    e_init,
    e_loss,
    bins=edges,
    range=log_range,
    statistic=mean_landau,
)
g4_std, _, _ = scipy.stats.binned_statistic(
    e_init,
    e_loss,
    bins=edges,
    range=log_range,
    statistic=fwhm_std_landau,
)
mid = 0.5 * (edges[:-1] + edges[1:])

# ax.hist(e_init, bins=edges, range=log_range, histtype="step")

ax.errorbar(mid, g4_mean, yerr=g4_std, fmt="o", linestyle="", label="Geant4")
#ax.plot(mid, g4_mean, marker="o", linestyle="", label="Geant4")

acts_eloss = pd.read_csv(f"{base_dir}/data/dense-propagation/acts/eloss_fe.csv")

acts_total_mean, _, _ = scipy.stats.binned_statistic(
    acts_eloss["p"],
    acts_eloss["total_mean"],
    bins=edges,
    range=log_range,
    statistic=mean,
)
acts_bethe_mean, _, _ = scipy.stats.binned_statistic(
    acts_eloss["p"],
    acts_eloss["bethe"],
    bins=edges,
    range=log_range,
    statistic=mean,
)
acts_landau_sigma, _, _ = scipy.stats.binned_statistic(
    acts_eloss["p"],
    acts_eloss["landau_sigma"],
    bins=edges,
    range=log_range,
    statistic=mean,
)

ax.errorbar(mid, acts_total_mean, yerr=acts_landau_sigma, fmt="o", linestyle="", label="ACTS")
# ax.plot(mid, acts_total_mean, label="ACTS")
# ax.plot(mid, acts_bethe, label="ACTS bethe")

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlabel("Initial momentum [GeV]")
ax.set_ylabel("Energy loss [GeV/mm]")

ax.legend()

if args.show:
    plt.show()

fig.savefig(f"{base_dir}/plots/dense-propagation/eloss_cmp.pdf", bbox_inches="tight")
