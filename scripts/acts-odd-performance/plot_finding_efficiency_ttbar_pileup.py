#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT
import atlasify

from mycommon.root import TH1


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("ttbar_pu0_finding_perf", type=Path)
parser.add_argument("ttbar_pu30_finding_perf", type=Path)
parser.add_argument("ttbar_pu60_finding_perf", type=Path)
parser.add_argument("ttbar_pu90_finding_perf", type=Path)
parser.add_argument("ttbar_pu120_finding_perf", type=Path)
parser.add_argument("ttbar_pu150_finding_perf", type=Path)
parser.add_argument("ttbar_pu200_finding_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

pus = [0, 30, 60, 90, 120, 150, 200]
finding_perf = [args.ttbar_pu0_finding_perf, args.ttbar_pu30_finding_perf, args.ttbar_pu60_finding_perf, args.ttbar_pu90_finding_perf, args.ttbar_pu120_finding_perf, args.ttbar_pu150_finding_perf, args.ttbar_pu200_finding_perf]
finding_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in finding_perf]

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"<$\mu$>")
ax.set_ylabel("Efficiency")

ax.set_xlim(0, 200)

ax.hlines(1, 0, 200, linestyles="--", color="gray")

eff = []
for pu, perf in zip(pus, finding_perf):
    eff_vs_eta = TH1(perf.Get("trackeff_vs_eta"), xrange=(-3, 3))
    eff.append(eff_vs_eta.y.mean())

ax.errorbar(pus, eff, fmt="o")

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="ACTS v40.0.0\n$t\\bar{t}$, $\\sqrt{s}$ = 14 TeV",
    enlarge=1.4,
)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
