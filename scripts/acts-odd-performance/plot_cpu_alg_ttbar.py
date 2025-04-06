#!/usr/bin/env python3

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import atlasify


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
algorithm_labels = [
    "Spacepoint formation",
    "Seeding",
    "Parameter estimation",
    "Track finding",
    "Ambiguity resolution",
    "Vertex finding",
]
show_algorithms = [
    False,
    True,
    False,
    True,
    False,
    True,
]

assert (
    len(selected_algorithms) == len(algorithm_labels) == len(show_algorithms)
), "equal number of algorithms and labels required"

rel_algorithm_times = []
for pu, input in zip(pus, args.inputs):
    times = pd.read_csv(input)
    algorithm_indices = {}
    alg_times = {}
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
            try:
                i = selected_algorithms.index(algorithm)
            except ValueError:
                i = selected_algorithms.index((algorithm, algorithm_index))
            alg_times[algorithm_labels[i]] = time_total_s
    rel_alg_times = {k: v / total for k, v in alg_times.items()}
    rel_algorithm_times.append(rel_alg_times)

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\langle \mu \rangle$")
ax.set_ylabel("Rel. CPU time")

width = 20
xs = np.array(pus) + width / 2
bottom = np.zeros(len(pus))
ys_others = np.zeros(len(pus))
for i, (algorithm_label, show) in enumerate(zip(algorithm_labels, show_algorithms)):
    ys = np.array(
        [
            times[algorithm_label] if algorithm_label in times else 0
            for times in rel_algorithm_times
        ]
    )

    if not show:
        ys_others += ys
        continue

    bar = ax.bar(
        xs,
        ys,
        width=width,
        bottom=bottom,
        label=algorithm_labels[i],
    )
    bottom += ys

    ax.bar_label(
        bar,
        labels=[f"{y:.2f}" if y >= 0.02 else "" for y in ys],
        label_type="center",
        fontsize=8,
        color="white",
        weight="bold",
    )
bar = ax.bar(
    xs,
    ys_others,
    width=width,
    bottom=bottom,
    label="Others",
)
bottom += ys_others
ax.bar_label(
    bar,
    labels=[f"{y:.2f}" if y >= 0.02 else "" for y in ys_others],
    label_type="center",
    fontsize=8,
    color="white",
    weight="bold",
)

ax.legend()

atlasify.atlasify(
    axes=ax,
    brand="ODD",
    atlas="Simulation",
    subtext="Acts v40.0.0\n$t\\bar{t}$, $\\sqrt{s}$ = 14 TeV",
    enlarge=1.5,
)

ax.set_xlim(0, 200 + width)
ylim = ax.get_ylim()
ax.set_ylim(0, ylim[1])

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
