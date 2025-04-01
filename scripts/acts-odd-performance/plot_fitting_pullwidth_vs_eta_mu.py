#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT

from mycommon.root import TH1


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("mu1GeV_fitting_perf", type=Path)
parser.add_argument("mu10GeV_fitting_perf", type=Path)
parser.add_argument("mu100GeV_fitting_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

pts = [1, 10, 100]
fitting_perf = [args.mu1GeV_fitting_perf, args.mu10GeV_fitting_perf, args.mu100GeV_fitting_perf]
fitting_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in fitting_perf]

params = ["d0", "z0", "phi", "theta", "qop", "t"]
ylabels = ["$d_0$", "$z_0$", r"$\phi$", r"$\theta$", "$q/p$", "$t$"]

fig, axs = plt.subplots(6, 1, figsize=(8, 6), sharex=True)

for ax, param, ylabel in zip(axs, params, ylabels):
    ax.hlines(1, -3, 3, linestyles="--", color="gray")

    ax.set_xlim(-3, 3)

    ax.set_xlabel(r"$\eta$")
    ax.set_ylabel(ylabel)

    for i, pt, perf in zip(range(3), pts, fitting_perf):
        pull_mean = TH1(perf.Get(f"pullwidth_{param}_vs_eta"), xrange=(-3, 3))

        pull_mean.errorbar(ax, fmt=".", label=f"{pt} GeV")

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
