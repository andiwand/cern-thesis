# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import curve_fit
import uproot
import awkward as ak
import numpy as np
import argparse


"""
input p = 1
output p = 0.769148
output std x = 58.9363
output std y = 58.9363
output std q/p = 0.0285193
output std p = 0.0168717
theta0 = 0.0392909
input p = 10
output p = 9.71864
output std x = 5.85906
output std y = 5.85906
output std q/p = 0.000173718
output std p = 0.016408
theta0 = 0.00390604
input p = 100
output p = 99.6298
output std x = 0.585871
output std y = 0.585871
output std q/p = 1.65276e-06
output std p = 0.0164055
theta0 = 0.000390581
"""


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


fig = plt.figure(figsize=(12, 8))
axs = fig.subplots(3, 3)

for axs_row, momentum, x_range, e_range, acts in zip(
    axs,
    [1, 10, 100],
    [(-220, 220), (-22, 22), (-2.2, 2.2)],
    [(0.65, 0.825), (9.55, 9.85), (99.55, 99.85)],
    [
        (0.769148, 0.0168717, 58.9363),
        (9.71864, 0.016408, 5.85906),
        (99.6298, 0.0164055, 0.585871),
    ],
):
    data = ak.to_dataframe(
        uproot.open(f"g4/data/chart_eloss_{momentum}GeV.root")["reading"].arrays(
            library="ak"
        )
    )

    x, y = data["x"], data["y"]
    e = data["e_final"]

    axs_row[0].hist2d(x, y, bins=50, range=(x_range, x_range), label="Geant4")
    axs_row[0].set_xlabel("x [mm]")
    axs_row[0].set_ylabel("y [mm]")

    _, bins, _ = axs_row[1].hist(
        x,
        density=True,
        bins=50,
        range=x_range,
        histtype="step",
        label=f"Geant4 σ={robust_std(x):.2f}",
    )
    axs_row[1].plot(bins, norm.pdf(bins, 0, acts[2]), label=f"ACTS σ={acts[2]:.2f}")
    axs_row[1].set_xlabel("x [mm]")
    axs_row[1].legend()

    _, bins, _ = axs_row[2].hist(
        e,
        density=True,
        bins=50,
        range=e_range,
        histtype="step",
        label=f"Geant4 µ={mean(e):.2f} σ={std(e):.2f}",
    )
    axs_row[2].axvline(x=mean(e), color="C0", linestyle="-")
    # axs_row[2].axvline(x=mean(e) - std(e), color="C0", linestyle="--")
    # axs_row[2].axvline(x=mean(e) + std(e), color="C0", linestyle="--")
    axs_row[2].axvline(
        x=acts[0], color="C1", linestyle="--", label=f"ACTS µ={acts[0]:.2f}"
    )
    # axs_row[2].plot(
    #    bins,
    #    norm.pdf(bins, acts[0], acts[1]),
    #    label=f"ACTS µ={acts[0]:.2f} σ={acts[1]:.2f}",
    # )
    axs_row[2].set_xlabel("E_final [GeV]")
    axs_row[2].legend()

plt.show()
