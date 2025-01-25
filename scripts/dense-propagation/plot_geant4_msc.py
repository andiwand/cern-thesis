# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import curve_fit
import uproot
import awkward as ak
import numpy as np
import argparse
from pathlib import Path


def mean(data):
    m = np.mean(data)
    return m


def std(data):
    s = np.std(data)
    return s


def robust_mean(data):
    (m, s), cov = robust_gauss_fit(data)
    return m


def robust_std(data):
    (m, s), cov = robust_gauss_fit(data)
    return s


def robust_gauss_fit_naive(data):
    def fit(data):
        return np.mean(data), np.std(data)

    if len(data) == 0:
        return (0, 0), np.zeros((2, 2))

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

    if len(data) == 0:
        return (0, 0), np.zeros((2, 2))

    for _ in range(3):
        (m, s), cov = fit(data)
        data = data[np.abs(data - m) < 3 * s]

    return (m, s), cov


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser(description="Plot multiple scattering")
parser.add_argument("--show", action="store_true", help="Show the plot")
args = parser.parse_args()

fig, axs = plt.subplots(2, 3, figsize=(8, 4), height_ratios=[2, 1], layout="constrained")

for i, axs_cols, momentum, x_range, e_range in zip(
    range(3),
    axs.T,
    [1, 10, 100],
    [(-220, 220), (-22, 22), (-2.2, 2.2)],
    [(0.65, 0.825), (9.55, 9.85), (99.55, 99.85)],
):
    data = ak.to_dataframe(
        uproot.open(f"{base_dir}/data/dense-propagation/chart_eloss_{momentum}GeV.root")["reading"].arrays(
            library="ak"
        )
    )

    x, y = data["x"], data["y"]
    e = data["e_final"]

    axs_cols[0].set_aspect("equal")
    axs_cols[0].set_title(f"{momentum} GeV")
    axs_cols[0].set_xlabel("x [mm]")
    if i == 0:
        axs_cols[0].set_ylabel("y [mm]")

    h2d = axs_cols[0].hist2d(x, y, bins=50, range=(x_range, x_range), vmin=0, vmax=60)

    (m, s), cov = robust_gauss_fit(x)

    # for j, c in zip(
    #     [1, 2, 3],
    #     ["r", "orange", "y"],
    # ):
    #     s_circle = plt.Circle((0, 0), j * s, color=f"{c}", fill=False, linestyle="--", label=f"{j} σ = {j * s:.2f} mm")
    #     axs_cols[0].add_artist(s_circle)
    # axs_cols[0].legend()

    axs_cols[1].sharex(axs_cols[0])
    axs_cols[1].set_xlabel("x [mm]")
    if i == 0:
        axs_cols[1].set_ylabel("hits")

    axs_cols[1].hist(x, bins=50, range=x_range, histtype="step", color="b")

    x_fit = np.linspace(*x_range, 1000)
    y_fit = norm.pdf(x_fit, m, s) * len(x) * (x_range[1] - x_range[0]) / 50
    axs_cols[1].plot(x_fit, y_fit, "r--", label=f"σ = {s:.2f} mm")

    # for j, c in zip(
    #     [1, 2, 3],
    #     ["r", "orange", "y"],
    # ):
    #     axs_cols[1].axvline(m + j * s, color=c, linestyle="--", label=f"{j} σ = {m + j * s:.2f} mm")
    #     axs_cols[1].axvline(m - j * s, color=c, linestyle="--")

    axs_cols[1].legend(loc="lower right")

fig.colorbar(h2d[3], ax=axs.ravel().tolist(), label="hits")

if args.show:
    plt.show()

plt.savefig(f"{base_dir}/plots/dense-propagation/geant4_msc.pdf", bbox_inches="tight")
