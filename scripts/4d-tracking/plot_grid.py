# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import uproot as up
import awkward as ak
import atlasify

from mycommon1.plots import get_color


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "--particles",
    type=Path,
    default=f"{base_dir}/data/4d-tracking/grid-density/particles.root",
    help="Path to the particles input file",
)
parser.add_argument(
    "--vertices",
    type=Path,
    default=f"{base_dir}/data/4d-tracking/grid-density/vertices.root",
    help="Path to the vertices input file",
)
parser.add_argument(
    "--grid-1d",
    type=Path,
    default=f"{base_dir}/data/4d-tracking/grid-density/grid-1d.csv",
    help="Path to the vertices input file",
)
parser.add_argument(
    "--grid-2d",
    type=Path,
    default=f"{base_dir}/data/4d-tracking/grid-density/grid-2d.csv",
    help="Path to the vertices input file",
)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/4d-tracking/ttbar-pu200-grid-density.pdf",
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()


vertices = ak.to_dataframe(
    up.open(args.vertices)["vertices"].arrays(
        ["event_id", "vz", "vt", "vertex_primary", "vertex_secondary", "generation"],
        library="ak",
    ),
    how="outer",
).dropna()
vertices = vertices[(vertices["vertex_secondary"] == 0)]

grid1d = pd.read_csv(args.grid_1d)
grid2d = pd.read_csv(args.grid_2d)

fig, axs = plt.subplots(2, 1, figsize=(8, 4), sharex=True, gridspec_kw={"height_ratios": [1, 10]})

# axs[0].set_title("Track density with $z_0$")
axs[0].get_yaxis().set_visible(False)
# axs[0].set_xlabel("z [mm]")

# axs[1].set_title("Track density with $z_0$ and $t_0$")

axs[1].set_xlabel("z [mm]")
axs[1].set_ylabel("t [mm]")

axs[0].set_aspect("auto")
axs[1].set_aspect("auto")

axs[0].set_xlim(-200, 200)
axs[1].set_xlim(-200, 200)

axs[0].hist2d(
    grid1d["z"],
    grid1d["t"],
    weights=grid1d["density"],
    norm=mcolors.PowerNorm(0.1),
    cmap=plt.cm.Blues,
    cmin=1,
    bins=(500, 1),
    range=((-200, 200), (-10, 10)),
)
axs[0].scatter(vertices["vz"], np.zeros(len(vertices)), s=1, c="red", label="truth")

counts, xedges, yedges, im = axs[1].hist2d(
    grid2d["z"],
    grid2d["t"],
    weights=grid2d["density"],
    norm=mcolors.PowerNorm(0.1),
    cmap=plt.cm.Blues,
    cmin=3,
    bins=(200, 100),
    range=((-200, 200), (-4000, 4000)),
)
axs[1].scatter(
    vertices["vz"],
    vertices["vt"],
    s=1,
    c="red",
    #label="Truth vertices",
)
"""
axs[1].legend(
    loc="upper right",
    #labelcolor="white",
    #edgecolor="white",
    fancybox=True,
    framealpha=0.5,
)
"""

atlasify.atlasify(
    axes=axs[0],
    outside=True,
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0\n$t\\bar{t}$, $\\sqrt{s}$ = 14 TeV, <$\\mu$> = 200",
    offset=18,
)
atlasify.atlasify(axes=axs[1], outside=True, atlas=False, offset=0)

cbar_ax = fig.add_axes([0.91, 0.12, 0.04, 0.63])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.set_ticks([])
cbar.set_label("Track density [a.u.]")

fig.subplots_adjust(left=0.1, bottom=0.12, right=0.88, top=0.75)

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
