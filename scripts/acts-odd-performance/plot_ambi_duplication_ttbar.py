#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT
import atlasify

from mycommon.root import TH1


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("ttbar_pu0_ambi_perf", type=Path)
parser.add_argument("ttbar_pu60_ambi_perf", type=Path)
parser.add_argument("ttbar_pu120_ambi_perf", type=Path)
parser.add_argument("ttbar_pu200_ambi_perf", type=Path)
parser.add_argument("ttbar_pu0_finding_perf", type=Path)
parser.add_argument("ttbar_pu60_finding_perf", type=Path)
parser.add_argument("ttbar_pu120_finding_perf", type=Path)
parser.add_argument("ttbar_pu200_finding_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

pus = [0, 60, 120, 200]
ambi_perf = [args.ttbar_pu0_ambi_perf, args.ttbar_pu60_ambi_perf, args.ttbar_pu120_ambi_perf, args.ttbar_pu200_ambi_perf]
ambi_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in ambi_perf]
finding_perf = [args.ttbar_pu0_finding_perf, args.ttbar_pu60_finding_perf, args.ttbar_pu120_finding_perf, args.ttbar_pu200_finding_perf]
finding_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in finding_perf]

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Duplicates")

ax.set_xlim(-3, 3)
ax.set_yscale("log")

for i, pu, aperf, fperf in zip(range(4), pus, ambi_perf, finding_perf):
    ambi_eff_vs_eta = TH1(aperf.Get("nDuplicated_vs_eta"), xrange=(-3, 3))
    finding_eff_vs_eta = TH1(fperf.Get("nDuplicated_vs_eta"), xrange=(-3, 3))

    ambi_eff_vs_eta.errorbar(ax, fmt="o", label=f"PU {pu}", color=f"C{i}")
    finding_eff_vs_eta.errorbar(ax, fmt="o", color=f"C{i}", alpha=0.5)

ax.legend()

ylim = ax.get_ylim()
ax.set_ylim(ylim[0], 1e2)

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="ACTS v40.0.0\n$t\\bar{t}$, $\\sqrt{s}$ = 14 TeV",
)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
