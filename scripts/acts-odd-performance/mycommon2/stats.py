import math
import numpy as np
import scipy.stats
import scipy.optimize
from collections.abc import Iterable


def robust_mean(data):
    (m, s), cov = robust_gauss_fit(data)
    return m


def robust_std(data):
    (m, s), cov = robust_gauss_fit(data)
    return s


def robust_std_std(data):
    (m, s), cov = robust_gauss_fit(data)
    return cov[1, 1] ** 0.5


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
        try:
            if len(data) < 20:
                raise ValueError(f"Not enough data to fit a Gaussian: {len(data)}")

            m, s = scipy.stats.norm.fit(data)

            hist_range = (m - 3 * s, m + 3 * s)
            bins = int(math.sqrt(len(data)))
            binned, edges = np.histogram(
                data, range=hist_range, bins=bins, density=True
            )
            centers = 0.5 * (edges[1:] + edges[:-1])

            params, cov = scipy.optimize.curve_fit(
                scipy.stats.norm.pdf, centers, binned, p0=(m, s), maxfev=1000000
            )
        except Exception as e:
            print(f"Falling back to naive mean/std. Error: {e}")
            params, cov = (np.mean(data), np.std(data)), np.zeros((2, 2))

        return params, cov

    (m, s), cov = (0, 0), np.zeros((2, 2))

    for _ in range(3):
        if len(data) == 0:
            return (m, s), cov

        (m, s), cov = fit(data)
        data = data[np.abs(data - m) < 3 * s]

    return (m, s), cov


def clopper_pearson(k, n, alpha=0.32):
    """
    http://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval
    alpha confidence intervals for a binomial distribution of k expected successes on n trials
    Clopper Pearson intervals are a conservative estimate.
    """
    p = k / n
    p_upper = np.maximum(
        scipy.stats.beta.ppf(1 - alpha / 2, k + 1, n - k), np.zeros_like(p)
    )
    p_lower = np.minimum(scipy.stats.beta.ppf(alpha / 2, k, n - k + 1), np.ones_like(p))
    if isinstance(p, Iterable):
        p_lower[p == 1.0], p_upper[p == 1.0] = 1.0, 1.0
    elif p == 1.0:
        p_lower, p_upper = 1.0, 1.0
    return p, p_upper, p_lower


def create_clopper_pearson_upper_bounds(alpha=0.32):
    def interval(data):
        _, p_upper, _ = clopper_pearson(np.sum(data), len(data), alpha)
        return p_upper

    return interval


def create_clopper_pearson_lower_bounds(alpha=0.32):
    def interval(data):
        _, _, p_lower = clopper_pearson(np.sum(data), len(data), alpha)
        return p_lower

    return interval


def line_fit(x, y, yerr):
    def line(x, a, b):
        return a * x + b

    popt, pcov = scipy.optimize.curve_fit(line, x, y, sigma=yerr, absolute_sigma=True)

    chi2sum = np.sum(((y - line(x, *popt)) / yerr) ** 2)
    ndf = len(x) - len(popt)
    p_value = 1 - scipy.stats.chi2.cdf(chi2sum, ndf)

    return popt, pcov, p_value
