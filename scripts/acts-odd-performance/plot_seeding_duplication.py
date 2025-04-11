#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT
import atlasify

from mycommon1.root import TH1
from mycommon1.plots import get_color, get_marker


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

ax.set_xlabel(r"true $\eta$")
ax.set_ylabel("Average duplication")

ax.set_xlim(-3, 3)

dupl_vs_eta = TH1(seeding_perf.Get("nDuplicated_vs_eta"), xrange=(-3, 3))
dupl_vs_eta.errorbar(ax, marker=get_marker(0), linestyle="", color=get_color(0))

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0\nsingle muons, <$\\mu$> = 0, $p_T$ = 1 GeV",
)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
