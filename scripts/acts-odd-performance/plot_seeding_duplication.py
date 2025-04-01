#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT
import atlasify

from mycommon.root import TH1


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("seeding_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

seeding_perf = ROOT.TFile.Open(args.seeding_perf.absolute().as_posix())

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Duplicates")

ax.set_xlim(-3, 3)

dupl_vs_eta = TH1(seeding_perf.Get("nDuplicated_vs_eta"), xrange=(-3, 3))
dupl_vs_eta.errorbar(ax, fmt="o")

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="ACTS v40.0.0\nsingle muons, <$\\mu$> = 0",
)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
