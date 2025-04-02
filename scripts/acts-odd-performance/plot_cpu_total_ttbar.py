#!/usr/bin/env python3

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import atlasify

from mycommon1.plots import get_color, get_marker


parser = argparse.ArgumentParser()
parser.add_argument("inputs", nargs="+")
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

pus = [0, 30, 60, 90, 120, 150, 200]

assert len(pus) == len(args.inputs), "equal number of inputs required"

selected_algorithms = [
    "Algorithm:SpacePointMaker",
    "Algorithm:SeedingAlgorithm",
    "Algorithm:TrackParamsEstimationAlgorithm",
    "Algorithm:TrackFindingAlgorithm",
    "Algorithm:GreedyAmbiguityResolutionAlgorithm",
    ("Algorithm:AdaptiveMultiVertexFinder", 0),
]

totals = []
for pu, input in zip(pus, args.inputs):
    times = pd.read_csv(input)
    algorithm_indices = {}
    total = 0
    for i, row in times.iterrows():
        algorithm, time_total_s = row["identifier"], row["time_total_s"]

        if algorithm not in algorithm_indices:
            algorithm_indices[algorithm] = 0
        else:
            algorithm_indices[algorithm] += 1
        algorithm_index = algorithm_indices[algorithm]

        if (
            algorithm in selected_algorithms
            or (algorithm, algorithm_index) in selected_algorithms
        ):
            total += time_total_s
    totals.append(total)
totals_rel = [total / totals[0] for total in totals]

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"<$\mu$>")
ax.set_ylabel("Rel. CPU time")

ax.plot(
    pus,
    totals_rel,
    marker=get_marker(0),
    linestyle="--",
    color=get_color(0),
    label="Reconstruction",
)

if True:
    # dashed line with linear extrapolation point 0 and 30
    k = (totals_rel[1] - totals_rel[0]) / (30 - 0)
    b = totals_rel[0] - k * 0
    xs = [0, 200]
    ys = [k * x + b for x in xs]
    ax.plot(
        xs,
        ys,
        linestyle="--",
        color="grey",
        label=f"Linear k={k:.2f}",
        zorder=-1,
    )

ax.legend()

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="ACTS v40.0.0\n$t\\bar{t}$, $\\sqrt{s}$ = 14 TeV",
)

ax.set_xlim(0, 200)
ylim = ax.get_ylim()
ax.set_ylim(0, ylim[1])

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
