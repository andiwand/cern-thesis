# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from common import read_g4_data, read_acts_data, make_g4_msc_stats, make_acts_msc_stats


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "--g4-input",
    nargs=3,
    type=Path,
    default=[
        f"{base_dir}/data/dense-propagation/geant4/logscale_mom_fe_{t}mm.root"
        for t in [10, 100, 1000]
    ],
    help="Path to Geant4 input file",
)
parser.add_argument(
    "--acts-input",
    nargs=3,
    type=Path,
    default=[
        f"{base_dir}/data/dense-propagation/acts/msc_eloss_fe_{t}mm.csv"
        for t in [10, 100, 1000]
    ],
    help="Path to ACTS input file",
)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/dense-propagation/msc_cmp_rel_stack.pdf",
    help="Path to output file",
)
parser.add_argument("--bins", type=int, default=20, help="Number of bins")
parser.add_argument("--e-range", nargs=2, default=[2, 300], help="Energy range in GeV")
parser.add_argument(
    "--min-p-out", type=float, default=2, help="Minimum output momentum"
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

labels = ["10 mm", "100 mm", "1000 mm"]

fig, axs = plt.subplots(
    3, 1, figsize=(8, 4), sharex=True, sharey=True, gridspec_kw={"hspace": 0.0}
)

# fig.suptitle("Relative positional uncertainty of muons passing Fe")
fig.supylabel("$\Delta$ position / ACTS")

for i, ax, label, g4_input, acts_input in zip(
    range(3), axs, labels, args.g4_input, args.acts_input
):
    ax.set_xlabel("Initial momentum [GeV]")
    ax.set_ylabel(label)

    log_range = (np.log10(args.e_range[0]), np.log10(args.e_range[1]))
    edges = 10 ** np.linspace(log_range[0], log_range[1], args.bins)
    mid = 0.5 * (edges[:-1] + edges[1:])

    if g4_input is not None:
        g4_data = read_g4_data(g4_input, args.min_p_out)
        g4_std, g4_std_std = make_g4_msc_stats(g4_data, edges, log_range)

    if acts_input is not None:
        acts_data = read_acts_data(acts_input, args.min_p_out)
        acts_std = make_acts_msc_stats(acts_data, edges, log_range)

    # ax.hlines(1, edges[0], edges[-1], linestyle="--", color="C0", label="Geant4")
    # ax.errorbar(mid, acts_std / g4_std, yerr=g4_std_std*(acts_std/g4_std**2), marker="o", linestyle="", color="C1", label="ACTS")

    ax.hlines(1, edges[0], edges[-1], linestyle="--", color="C1", label="ACTS")
    ax.errorbar(
        mid,
        g4_std / acts_std,
        yerr=g4_std_std * (1 / acts_std),
        marker="o",
        linestyle="",
        color="C0",
        label="Geant4",
    )

    ax.set_xscale("log")
    ax.set_xlim(edges[0], edges[-1])

    if i == 0:
        ax.legend(loc="lower right")

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
