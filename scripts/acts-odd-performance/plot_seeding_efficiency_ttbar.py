#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT

from mycommon.root import TH1


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("ttbar_pu0_seeding_perf", type=Path)
parser.add_argument("ttbar_pu60_seeding_perf", type=Path)
parser.add_argument("ttbar_pu120_seeding_perf", type=Path)
parser.add_argument("ttbar_pu200_seeding_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

pus = [0, 60, 120, 200]
seeding_perf = [args.ttbar_pu0_seeding_perf, args.ttbar_pu60_seeding_perf, args.ttbar_pu120_seeding_perf, args.ttbar_pu200_seeding_perf]
seeding_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in seeding_perf]

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Efficiency")

ax.set_xlim(-3, 3)

ax.hlines(1, -3, 3, linestyles="--", color="gray")

for pu, perf in zip(pus, seeding_perf):
    eff_vs_eta = TH1(perf.Get("trackeff_vs_eta"), xrange=(-3, 3))
    eff_vs_eta.errorbar(ax, fmt="o", label=f"PU {pu}")

ax.legend()

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
