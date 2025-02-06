import uproot
import awkward as ak
import numpy as np
import pandas as pd
import scipy.stats
from scipy.optimize import curve_fit


def read_g4_data(path, min_p_out):
    g4_data = ak.to_dataframe(
        uproot.open(path)["reading"].arrays(library="ak")
    )
    g4_data = g4_data[g4_data["e_final"] > min_p_out]

    return g4_data


def read_acts_data(path, min_p_out):
    acts_data = pd.read_csv(path)
    acts_data = acts_data[acts_data["p_final"] > min_p_out]

    return acts_data



def make_g4_stats(g4_data, edges, log_range):
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

    return g4_std, g4_std_std


def make_acts_stats(acts_data, edges, log_range):
    acts_std, _, _ = scipy.stats.binned_statistic(
        acts_data["p_initial"],
        acts_data["sigma"],
        bins=edges,
        range=log_range,
        statistic=stat_mean,
    )

    return acts_std


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
