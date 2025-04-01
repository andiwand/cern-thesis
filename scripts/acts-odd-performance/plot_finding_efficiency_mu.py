#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT

from mycommon.root import TH1


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("mu1GeV_finding_perf", type=Path)
parser.add_argument("mu10GeV_finding_perf", type=Path)
parser.add_argument("mu100GeV_finding_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

pts = [1, 10, 100]
finding_perf = [args.mu1GeV_finding_perf, args.mu10GeV_finding_perf, args.mu100GeV_finding_perf]
finding_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in finding_perf]

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Efficiency")

ax.set_xlim(-3, 3)

ax.hlines(1, -3, 3, linestyles="--", color="gray")

for i, pt, perf in zip(range(3), pts, finding_perf):
    eff_vs_eta = TH1(perf.Get("trackeff_vs_eta"), xrange=(-3, 3))
    eff_vs_eta.errorbar(ax, fmt="o", label=f"{pt} GeV", color=f"C{i}")

ax.legend()

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
