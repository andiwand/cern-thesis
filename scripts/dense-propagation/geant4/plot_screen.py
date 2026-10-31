# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.stats import norm
import numpy as np
import atlasify


def material_label(material):
    if material == "fe":
        return "Fe"
    if material == "lar":
        return "LAr"
    raise ValueError(f"Unknown material: {material}")


import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import read_g4_data, robust_gauss_fit


base_dir = Path(__file__).parent.parent.parent.parent

parser = argparse.ArgumentParser(description="Plot multiple scattering")
parser.add_argument(
    "material",
    type=str,
    choices=["fe", "lar"],
)
parser.add_argument(
    "thickness",
    type=int,
    help="Thickness in mm",
)
parser.add_argument(
    "--input",
    nargs=3,
    type=Path,
    help="Path to the input files",
)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

fig, axs = plt.subplots(
    2, 3, figsize=(8, 4.5), height_ratios=[2, 1], layout="constrained"
)

# fig.suptitle("Recorded positions with muons passing 1 m of LAr")

for i, file, axs_cols, momentum, x_range, e_range in zip(
    range(3),
    args.input,
    axs.T,
    [1, 10, 100],
    [(-220, 220), (-22, 22), (-2.2, 2.2)],
    [(0.65, 0.825), (9.55, 9.85), (99.55, 99.85)],
):
    data = read_g4_data(file, 0)

    x, y = data["x"], data["y"]
    e = data["p_final"]

    # axs_cols[0].set_aspect("equal")
    axs_cols[0].set_title(f"p = {data['p_initial'].mean():.3g} GeV")
    # axs_cols[0].set_xlabel("x [mm]")
    if i == 0:
        axs_cols[0].set_ylabel("y [mm]")

    h2d = axs_cols[0].hist2d(
        x, y, bins=50, range=(x_range, x_range), vmin=0, vmax=60, cmap="Blues", cmin=10
    )

    (m, s), cov = robust_gauss_fit(x)

    # for j, c in zip(
    #     [1, 2, 3],
    #     ["r", "orange", "y"],
    # ):
    #     s_circle = plt.Circle((0, 0), j * s, color=f"{c}", fill=False, linestyle="--", label=f"{j} σ = {j * s:.2f} mm")
    #     axs_cols[0].add_artist(s_circle)
    # axs_cols[0].legend()

    axs_cols[1].sharex(axs_cols[0])
    axs_cols[1].set_xlabel("x [mm]")
    if i == 0:
        axs_cols[1].set_ylabel("hits")

    axs_cols[1].hist(x, bins=50, range=x_range, histtype="step", color="b")

    x_fit = np.linspace(*x_range, 1000)
    y_fit = norm.pdf(x_fit, m, s) * len(x) * (x_range[1] - x_range[0]) / 50
    axs_cols[1].plot(x_fit, y_fit, "r--", label=f"σ = {s:.2f} mm")

    # for j, c in zip(
    #     [1, 2, 3],
    #     ["r", "orange", "y"],
    # ):
    #     axs_cols[1].axvline(m + j * s, color=c, linestyle="--", label=f"{j} σ = {m + j * s:.2f} mm")
    #     axs_cols[1].axvline(m - j * s, color=c, linestyle="--")

    atlasify.atlasify(axes=axs_cols[0], outside=True, atlas=False, offset=0)
    atlasify.atlasify(axes=axs_cols[1], outside=True, atlas=False, offset=0)

    axs_cols[1].legend(loc="lower right")

cbar = fig.colorbar(h2d[3], ax=axs.ravel().tolist())
cbar.set_ticks([])
cbar.set_label("Hit density [a.u.]")

fig.suptitle("\n\n\n\n")

ax = fig.add_axes([0.06, 0.0, 0.94, 1.0])
ax.axis("off")
atlasify.atlasify(
    axes=ax,
    brand="ACTS",
    atlas="Simulation",
    subtext=f"ACTS v40.0.0\nsingle muons in {args.thickness} mm of {material_label(args.material)}",
)

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
