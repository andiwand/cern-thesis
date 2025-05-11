#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot
import pandas as pd
import awkward as ak
import matplotlib.pyplot as plt
import atlasify

from mycommon1.plots import get_color, get_marker
from mycommon2.stats import clopper_pearson


columns = [
    "vertex_primary",
    "vertex_secondary",
    "nTrueVtx",
    "nVtxReconstructable",
    "nCleanVtx",
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "--inputs-wot", required=True, nargs="+", help="input files without time"
)
parser.add_argument(
    "--inputs-wt", required=True, nargs="+", help="input files with time"
)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

inputs = {
    "without time": args.inputs_wot,
    "with time": args.inputs_wt,
}
pus = [0, 30, 60, 90, 120, 150, 200]

assert (
    len(pus) == len(args.inputs_wot) == len(args.inputs_wt)
), "equal number of inputs required"

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

results = {input_type: [] for input_type in inputs.keys()}

for input_type, inputs_list in inputs.items():
    for input, pu in zip(inputs_list, pus):
        data = ak.to_dataframe(
            uproot.open(input)["vertexing"].arrays(columns, library="ak"),
            how="outer",
        )

        # filter for first primary vertex which is the HS vertex by design
        data = data[(data["vertex_primary"] == 1) & (data["vertex_secondary"] == 0)]

        eff, eff_err_upper, eff_err_lower = clopper_pearson(data["nCleanVtx"].sum(), data["nVtxReconstructable"].sum())

        results[input_type].append(
            {
                "pu": pu,
                "eff": eff,
                "eff_err_low": eff - eff_err_lower,
                "eff_err_high": eff_err_upper - eff,
            }
        )

ax.set_xlabel(r"$\langle \mu \rangle$")
ax.set_ylabel("Technical efficiency")

ax.set_xlim(-5, 205)

ax.hlines(1, -5, 205, linestyles="--", color="gray")

for i, input_type in enumerate(inputs.keys()):
    data = pd.DataFrame(results[input_type])

    ax.errorbar(
        data["pu"],
        data["eff"],
        yerr=(data["eff_err_low"], data["eff_err_high"]),
        label=f"{input_type}",
        marker=get_marker(i),
        linestyle="",
        color=get_color(i),
    )

ax.legend()

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
