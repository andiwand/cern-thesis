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
    type=Path,
    default=f"{base_dir}/data/dense-propagation/geant4/logscale_mom_fe_100mm.root",
    help="Path to Geant4 input file",
)
parser.add_argument(
    "--acts-input",
    type=Path,
    default=f"{base_dir}/data/dense-propagation/acts/msc_eloss_fe_100mm.csv",
    help="Path to ACTS input file",
)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/dense-propagation/msc_cmp_rel.pdf",
    help="Path to output file",
)
parser.add_argument("--bins", type=int, default=30, help="Number of bins")
parser.add_argument(
    "--e-range", nargs=2, default=[2, 300], help="Energy range in GeV"
)
parser.add_argument("--min-p-out", type=float, default=2, help="Minimum output momentum")
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_title("Relative positional uncertainty of muons passing 100 mm Fe")
ax.set_xlabel("Initial momentum [GeV]")
ax.set_ylabel("Relative positional uncertainty")

log_range = (np.log10(args.e_range[0]), np.log10(args.e_range[1]))
edges = 10 ** np.linspace(log_range[0], log_range[1], args.bins)
mid = 0.5 * (edges[:-1] + edges[1:])

if args.g4_input is not None:
    g4_data = read_g4_data(args.g4_input, args.min_p_out)
    g4_std, g4_std_std = make_g4_msc_stats(g4_data, edges, log_range)

if args.acts_input is not None:
    acts_data = read_acts_data(args.acts_input, args.min_p_out)
    acts_std = make_acts_msc_stats(acts_data, edges, log_range)

ax.hlines(1, edges[0], edges[-1], linestyle="--", color="black", label="Geant4")
ax.plot(mid, acts_std / g4_std, marker="o", linestyle="", label="ACTS")

ax.set_xscale("log")

ax.legend()

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
