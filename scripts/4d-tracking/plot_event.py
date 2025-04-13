# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot
import numpy as np
import awkward as ak
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import atlasify


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "--particles",
    type=Path,
    default=f"{base_dir}/data/4d-tracking/ttbar-pu200-particles.root",
    help="Path to the particles input file",
)
parser.add_argument(
    "--vertices",
    type=Path,
    default=f"{base_dir}/data/4d-tracking/ttbar-pu200-vertices.root",
    help="Path to the vertices input file",
)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/4d-tracking/ttbar-pu200-event-display.pdf",
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

fig, axs = plt.subplots(2, 2, figsize=(8, 6))

particles = ak.to_dataframe(
    uproot.open(args.particles)["particles"].arrays(library="ak")
)
particles = particles[
    (particles["q"].abs() == 1) & (particles["pt"] > 1) & (particles["eta"].abs() < 3.0)
]


def project_to_xy(p):
    return np.vstack([p[:, 2], np.linalg.norm(p[:, :2], axis=1) * np.sign(p[:, 0])]).T


def time_to_color(t):
    return (t + 2000) / 4000


vertices = ak.to_dataframe(
    uproot.open(args.vertices)["vertices"].arrays(
        ["vx", "vy", "vz", "vt", "vertex_primary", "vertex_secondary", "generation"],
        library="ak",
    )
)
vertices = vertices[(vertices["vertex_secondary"] == 0)]
vertices["c"] = time_to_color(vertices["vt"])

lines = pd.DataFrame(columns=["x0", "y0", "z0", "t0", "x1", "y1", "z1", "c"])
lines[["x0", "y0", "z0", "t0"]] = particles[["vx", "vy", "vz", "vt"]]
directions = (
    particles[["px", "py", "pz"]].values
    / np.linalg.norm(particles[["px", "py", "pz"]].values, axis=1)[:, np.newaxis]
)
lines[["x1", "y1", "z1"]] = lines[["x0", "y0", "z0"]] + 1000 * directions
lines["c"] = time_to_color(lines["t0"])

vertices[["px", "py"]] = project_to_xy(vertices[["vx", "vy", "vz"]].values)
lines[["px0", "py0"]] = project_to_xy(lines[["x0", "y0", "z0"]].values)
lines[["px1", "py1"]] = project_to_xy(lines[["x1", "y1", "z1"]].values)

for i, ax in np.ndenumerate(axs):
    for _, line in lines.iterrows():
        ax.plot(
            line[["px0", "px1"]],
            line[["py0", "py1"]],
            color="black" if i[0] == 0 else cm.seismic(line["c"]),
            alpha=0.5,
        )

    ax.scatter(
        vertices["px"],
        vertices["py"],
        color="red" if i[0] == 0 else cm.seismic(vertices["c"]),
        marker=".",
        s=60,
        zorder=10,
    )

    ax.scatter(
        vertices.iloc[0]["px"],
        vertices.iloc[0]["py"],
        facecolors="none",
        edgecolors="blue",
        linewidths=3,
        s=60,
        zorder=20,
    )

for i in range(2):
    axs[i, 0].set_xlim(-250, 250)
    axs[i, 0].set_ylim(-100, 100)

    axs[i, 1].set_xlim(vertices.iloc[0]["vz"] - 10, vertices.iloc[0]["vz"] + 10)
    axs[i, 1].set_ylim(-10, 10)

    axs[1, i].set_xlabel("z [mm]")
    axs[i, 0].set_ylabel("R $\\cdot$ sign(x) [mm]")

atlasify.atlasify(
    axes=axs[0, 0],
    outside=True,
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0\n$t\\bar{t}$, $\\sqrt{s}$ = 14 TeV, <$\\mu$> = 200",
    offset=18,
)
atlasify.atlasify(axes=axs[0, 1], outside=True, atlas=False, offset=0)
atlasify.atlasify(axes=axs[1, 0], outside=True, atlas=False, offset=0)
atlasify.atlasify(axes=axs[1, 1], outside=True, atlas=False, offset=0)

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
