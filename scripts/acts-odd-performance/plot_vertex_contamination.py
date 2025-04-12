#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot
import awkward as ak
import matplotlib.pyplot as plt
import atlasify
import matplotlib.patches as mpatches

from mycommon1.plots import get_color


columns = [
    "vertex_primary",
    "vertex_secondary",
    "recoVertexContamination",
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

        contamination = data["recoVertexContamination"]
        contamination = contamination[contamination > 0]

        results[input_type].append(
            {
                "pu": pu,
                "contaminations": contamination.values,
            }
        )

for i, input_type in enumerate(inputs.keys()):
    for result in results[input_type]:
        pu = result["pu"]
        contamination = result["contaminations"]

        # make violin plots side by side
        violin_parts = ax.violinplot(
            [contamination],
            positions=[pu],
            widths=20,
            side="low" if i == 0 else "high",
            showmeans=True,
            showmedians=True,
            showextrema=True,
        )

        for partname in ["cbars", "cmins", "cmaxes", "cmeans", "cmedians"]:
            if partname not in violin_parts:
                continue
            vp = violin_parts[partname]
            vp.set_edgecolor(get_color(i))
            vp.set_linewidth(1)
        for vp in violin_parts["bodies"]:
            vp.set_facecolor(get_color(i))
            vp.set_edgecolor(get_color(i))
            vp.set_linewidth(1)
            vp.set_alpha(0.5)

labels = [
    (mpatches.Patch(color=get_color(0),alpha=0.5), "without time"),
    (mpatches.Patch(color=get_color(1),alpha=0.5), "with time"),
]
ax.legend(*zip(*labels))

ax.set_xlabel(r"$\langle \mu \rangle$")
ax.set_ylabel("Vertex contamination")

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0\n$t\\bar{t}$, $\\sqrt{s}$ = 14 TeV",
)

ax.set_xlim(-15, 215)
ylim = ax.get_ylim()
ax.set_ylim(0, ylim[1])

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
