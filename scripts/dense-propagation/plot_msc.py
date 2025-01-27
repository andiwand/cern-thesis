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
from scipy.optimize import curve_fit


def robust_gauss_fit_naive(data):
    def fit(data):
        return np.mean(data), np.std(data)

    for _ in range(3):
        m, s = fit(data)
        data = data[np.abs(data - np.median(data)) < 3 * s]

    return (m, s), np.zeros((2, 2))


def robust_gauss_fit(data):
    def fit(data):
        def gauss(x, m, s):
            return 1 / (s * (2 * np.pi) ** 0.5) * np.exp(-0.5 * ((x - m) / s) ** 2)

        try:
            if len(data) < 20:
                raise ValueError(f"Not enough data to fit a Gaussian: {len(data)}")

            low, mp1s, median, mm1s, high = np.percentile(data, [1, 16, 50, 84, 99])
            hist_range = (low, high)
            bins = 30
            binned, edges = np.histogram(
                data, range=hist_range, bins=bins, density=True
            )
            centers = 0.5 * (edges[1:] + edges[:-1])

            p0 = median, mm1s - mp1s
            params, cov = curve_fit(gauss, centers, binned, p0=p0, maxfev=1000000)

            if cov[1, 1] > 5 * params[1] ** 2:
                raise ValueError(
                    f"Fit failed, covariance too large: {cov[1, 1]} > {5 * params[1] ** 2}"
                )
        except Exception as e:
            print(f"Falling back to naive mean/std. Error: {e}")
            params, cov = (np.mean(data), np.std(data)), np.zeros((2, 2))

        return params, cov

    for _ in range(3):
        (m, s), cov = fit(data)
        data = data[np.abs(data - m) < 3 * s]

    return (m, s), cov


def stat_mean(data):
    if len(data) == 0:
        return None
    return np.mean(data)


def stat_robust_std(data):
    if len(data) == 0:
        return None
    (_, s), _ = robust_gauss_fit(data)
    return s


def stat_robust_std_std(data):
    if len(data) == 0:
        return None
    (_, _), cov = robust_gauss_fit(data)
    return np.sqrt(cov[1, 1])


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
    default=f"{base_dir}/data/dense-propagation/acts/msc_fe.csv",
    help="Path to ACTS input file",
)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/dense-propagation/msc_cmp.pdf",
    help="Path to output file",
)
parser.add_argument("--bins", type=int, default=30, help="Number of bins")
parser.add_argument(
    "--e-range", nargs=2, default=[0.05, 300], help="Energy range in GeV"
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_title("Positional uncertainty of muons passing 100 mm Fe")
ax.set_xlabel("Initial momentum [GeV]")
ax.set_ylabel("Positional uncertainty [mm]")

log_range = (np.log10(args.e_range[0]), np.log10(args.e_range[1]))
edges = 10 ** np.linspace(log_range[0], log_range[1], args.bins)
mid = 0.5 * (edges[:-1] + edges[1:])

if args.g4_input is not None:
    g4_data = ak.to_dataframe(
        uproot.open(args.g4_input)["reading"].arrays(library="ak")
    )

    g4_e_init = g4_data["e_init"]
    g4_x = g4_data["x"]

    g4_std, _, _ = scipy.stats.binned_statistic(
        g4_e_init,
        g4_x,
        bins=edges,
        range=log_range,
        statistic=stat_robust_std,
    )
    g4_std_std, _, _ = scipy.stats.binned_statistic(
        g4_e_init,
        g4_x,
        bins=edges,
        range=log_range,
        statistic=stat_robust_std_std,
    )

    ax.errorbar(mid, g4_std, yerr=g4_std_std, marker="o", linestyle="", label="Geant4")

if args.acts_input is not None:
    acts_data = pd.read_csv(args.acts_input)

    acts_std, _, _ = scipy.stats.binned_statistic(
        acts_data["p_initial"],
        acts_data["sigma"],
        bins=edges,
        range=log_range,
        statistic=stat_mean,
    )

    ax.plot(mid, acts_std, marker="^", linestyle="", label="ACTS")

ax.set_xscale("log")
ax.set_yscale("log")

ax.legend()

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
