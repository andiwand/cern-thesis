#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT

from mycommon.root import TH1


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("mu_fitting_perf", type=Path)
parser.add_argument("pi_fitting_perf", type=Path)
parser.add_argument("e_fitting_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

ptypes = ["mu", "pi", "e"]
fitting_perf = [args.mu_fitting_perf, args.pi_fitting_perf, args.e_fitting_perf]
fitting_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in fitting_perf]

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$p_T$ [GeV]")
ax.set_ylabel(r"$\sigma_{z_0}$ [mm]")

for i, ptype, perf in zip(range(3), ptypes, fitting_perf):
    eff_vs_eta = TH1(perf.Get("reswidth_z0_vs_pT"))
    eff_vs_eta.errorbar(ax, fmt="o", label=f"{ptype}")

ax.legend()

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
