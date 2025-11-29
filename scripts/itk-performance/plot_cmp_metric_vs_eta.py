#!/usr/bin/env python3

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import ROOT
import atlasify

from mycommon1.root import TH1
from mycommon1.plots import get_color, get_marker
from mycommon1.stats import ratio_std


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("event", choices=["single_mu", "ttbar"], help="Event kind")
parser.add_argument("metric", choices=["eff", "fake"])
parser.add_argument("input_acts", type=Path)
parser.add_argument("input_legacy", type=Path)
parser.add_argument("--input-acts-mod", type=Path)
parser.add_argument("--pt", type=int, default=2)
parser.add_argument("--pu", type=int, default=0)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

idpvm_acts = ROOT.TFile.Open(args.input_acts.absolute().as_posix())
idpvm_legacy = ROOT.TFile.Open(args.input_legacy.absolute().as_posix())
idpvm_acts_mod = (
    ROOT.TFile.Open(args.input_acts_mod.absolute().as_posix())
    if args.input_acts_mod
    else None
)

fig, axs = plt.subplots(
    2,
    1,
    figsize=(8, 4),
    layout="compressed",
    sharex=True,
    gridspec_kw={"hspace": 0.05, "height_ratios": [4, 1]},
)

if args.metric == "eff":
    path = "SquirrelPlots/Tracks/Efficiency/technical_efficiency_vs_eta"
    axs[0].set_ylabel(r"Technical efficiency")
elif args.metric == "fake":
    path = "SquirrelPlots/Tracks/FakeRate/fakerate_vs_eta"
    axs[0].set_ylabel(r"Fake ratio")
else:
    raise ValueError(f"Unknown metric: {args.metric}")

axs[1].set_xlabel(r"true $\eta$")
axs[1].set_ylabel(r"Ratio")

axs[0].set_xlim(-4, 4)

if args.metric == "fake":
    axs[0].set_yscale("log")
    axs[1].set_yscale("log")

if args.metric == "eff":
    axs[0].hlines(1, -4, 4, linestyles="--", color="gray")

acts_res_vs_eta = TH1(
    idpvm_acts.Get(path),
    xrange=(-4, 4),
)
acts_res_vs_eta.errorbar(
    axs[0],
    label=f"ACTS-based",
    marker=get_marker(0),
    linestyle="",
    color=get_color(0),
)

legacy_res_vs_eta = TH1(
    idpvm_legacy.Get(path),
    xrange=(-4, 4),
)
legacy_res_vs_eta.errorbar(
    axs[0],
    label=f"Legacy",
    marker=get_marker(1),
    linestyle="",
    color=get_color(1),
)

axs[1].errorbar(
    x=legacy_res_vs_eta.x,
    y=np.ones_like(legacy_res_vs_eta.y),
    xerr=acts_res_vs_eta.x_err_lo,
    # label="Legacy",
    marker=get_marker(1),
    linestyle="",
    color=get_color(1),
)

axs[1].errorbar(
    x=acts_res_vs_eta.x,
    y=acts_res_vs_eta.y / legacy_res_vs_eta.y,
    xerr=acts_res_vs_eta.x_err_lo,
    yerr=ratio_std(
        acts_res_vs_eta.y,
        legacy_res_vs_eta.y,
        acts_res_vs_eta.y_err_lo,
        legacy_res_vs_eta.y_err_lo,
    ),
    # label="ACTS-based",
    marker=get_marker(0),
    linestyle="",
    color=get_color(0),
)

if idpvm_acts_mod:
    acts_mod_res_vs_eta = TH1(
        idpvm_acts_mod.Get(path),
        xrange=(-4, 4),
    )
    acts_mod_res_vs_eta.errorbar(
        axs[0],
        label=f"ACTS-based modified",
        marker=get_marker(2),
        linestyle="",
        color=get_color(2),
    )

    axs[1].errorbar(
        x=acts_mod_res_vs_eta.x,
        y=acts_mod_res_vs_eta.y / legacy_res_vs_eta.y,
        xerr=acts_mod_res_vs_eta.x_err_lo,
        yerr=ratio_std(
            acts_mod_res_vs_eta.y,
            legacy_res_vs_eta.y,
            acts_mod_res_vs_eta.y_err_lo,
            legacy_res_vs_eta.y_err_lo,
        ),
        # label="ACTS-based modified",
        marker=get_marker(2),
        linestyle="",
        color=get_color(2),
    )

axs[0].legend()

if args.event == "single_mu":
    subtext = (
        f"Athena 25.0.30\nsingle muons, $p_T$ = {args.pt} GeV, <$\\mu$> = {args.pu}"
    )
elif args.event == "ttbar":
    subtext = (
        f"Athena 25.0.30\n$t\\bar{{t}}$, $\\sqrt{{s}}$ = 14 TeV, <$\\mu$> = {args.pu}"
    )
else:
    raise ValueError(f"Unknown event: {args.event}")

atlasify.atlasify(
    axes=axs[0],
    brand="ITk",
    atlas="Simulation",
    subtext=subtext,
    enlarge=1.4,
)
atlasify.atlasify(axes=axs[1], outside=True, atlas=False, offset=0)

if args.metric == "fake":
    ylim = axs[0].get_ylim()
    axs[0].set_ylim(ylim[0], ylim[1] * 15)

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
