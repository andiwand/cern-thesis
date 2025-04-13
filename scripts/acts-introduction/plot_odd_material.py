#!/usr/bin/env python3

import uproot
import matplotlib.pyplot as plt
import mplhep
import argparse
from pathlib import Path
import atlasify


parser = argparse.ArgumentParser()
parser.add_argument("x", choices=["phi", "eta"])
parser.add_argument("y", choices=["x0", "l0"])
parser.add_argument("input", type=Path, help="Material composition file")
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

names = {
    "all": "Full detector",
    "beampipe": "Beam pipe",
    "sstrips": "Short Strips",
    "lstrips": "Long Strips",
    "pixel": "Pixel",
    "solenoid": "Solenoid",
    "ecal": "EM Calorimeter",
}
region_order = ["beampipe", "pixel", "sstrips", "lstrips"]
region_labels = ["Beampipe", "Pixel", "Short Strips", "Long Strips"]

x_label = {"phi": r"$\phi$", "eta": r"$\eta$"}[args.x]
y_label = {"l0": r"$X/\lambda_0$", "x0": "$X/X_0$"}[args.y]

hists = []
labels = []

rf = uproot.open(args.input)

for name, label in zip(region_order, region_labels):
    key = f"{name}_{args.y}_vs_{args.x}_all"
    if key in rf:
        o = rf[key].to_hist()
        o.axes[0].label = args.x
        hists.append(o)
    else:
        print(f"Key {key} not found in {args.input}")
    labels.append(label)

fig, ax = plt.subplots(1, 1, figsize=(8, 4), layout="compressed")
mplhep.histplot(hists, ax=ax, stack=True, histtype="fill", label=labels)
ax.set_xlim(hists[0].axes[0].edges[0], hists[0].axes[0].edges[-1])
ax.set_xlabel(x_label)
ax.set_ylabel(y_label)
ax.legend()

if args.x == "eta":
    ymin, ymax = ax.get_ylim()
    ax.vlines(
        [-3, 3],
        ymin,
        ymax,
        color="black",
        linestyle="--",
    )

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0",
    enlarge=1.3,
)

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
