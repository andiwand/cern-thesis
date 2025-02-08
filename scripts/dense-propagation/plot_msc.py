# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from common import (
    read_g4_data,
    read_acts_data,
    make_g4_msc_stats,
    make_acts_msc_stats,
    stat_robust_std,
)


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
    default=f"{base_dir}/plots/dense-propagation/msc_cmp.pdf",
    help="Path to output file",
)
parser.add_argument("--bins", type=int, default=30, help="Number of bins")
parser.add_argument("--e-range", nargs=2, default=[2, 300], help="Energy range in GeV")
parser.add_argument(
    "--min-p-out", type=float, default=2, help="Minimum output momentum"
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

# ax.set_title("Positional uncertainty of muons passing 100 mm Fe")
ax.set_xlabel("Initial momentum [GeV]")
ax.set_ylabel("Positional uncertainty [mm]")

log_range = (np.log10(args.e_range[0]), np.log10(args.e_range[1]))
edges = 10 ** np.linspace(log_range[0], log_range[1], args.bins)
mid = 0.5 * (edges[:-1] + edges[1:])

if args.g4_input is not None:
    g4_data = read_g4_data(args.g4_input, args.min_p_out)
    g4_std, g4_std_std = make_g4_msc_stats(g4_data, edges, log_range)

    ax.errorbar(mid, g4_std, yerr=g4_std_std, marker="o", linestyle="", label="Geant4")

if args.acts_input is not None:
    acts_data = read_acts_data(args.acts_input, args.min_p_out)
    acts_std = make_acts_msc_stats(acts_data, edges, log_range)

    ax.plot(mid, acts_std, marker="^", linestyle="", label="ACTS")

ax.set_xscale("log")
ax.set_yscale("log")

ax.legend()

for p_min, p_max in [
    (290, 310),
    # (0.9, 1.1),
]:
    import scipy.stats

    ofig, oaxs = plt.subplots(1, 2, figsize=(4, 3))
    g4_mask = (g4_data["p_initial"] > p_min) & (g4_data["p_initial"] < p_max)
    g4_data = g4_data[g4_mask]
    acts_mask = (acts_data["p_initial"] > p_min) & (acts_data["p_initial"] < p_max)
    acts_data = acts_data[acts_mask]

    oaxs[0].hist(g4_data["x"], bins=100, histtype="step", label="Geant4", density=True)

    acts_xs = np.linspace(g4_data["x"].min(), g4_data["x"].max(), 300)
    oaxs[0].plot(
        acts_xs,
        scipy.stats.norm.pdf(acts_xs, 0, np.mean(acts_data["x_sigma"])),
        label="ACTS",
    )

    print("pos")
    print(f"Geant4: {np.mean(g4_data['x']):.2f} ± {np.std(g4_data['x']):.2f}")
    print(f"Geant4 fit: {stat_robust_std(g4_data['x']):.2f}")
    print(f"ACTS: 0 ± {np.mean(acts_data['x_sigma']):.2f}")

    oaxs[0].legend()

    oaxs[1].hist(
        g4_data["dir1"], bins=100, histtype="step", label="Geant4", density=True
    )

    acts_xs = np.linspace(g4_data["dir1"].min(), g4_data["dir1"].max(), 300)
    oaxs[1].plot(
        acts_xs,
        scipy.stats.norm.pdf(acts_xs, 0, np.mean(acts_data["dir_sigma"])),
        label="ACTS",
    )

    print("dir")
    print(f"Geant4: {np.mean(g4_data['dir1'])} ± {np.std(g4_data['dir1'])}")
    print(f"Geant4 fit: {stat_robust_std(g4_data['dir1'])}")
    print(f"ACTS: 0 ± {np.mean(acts_data['dir_sigma'])}")

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
