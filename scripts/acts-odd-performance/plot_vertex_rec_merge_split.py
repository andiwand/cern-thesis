#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot
import numpy as np
import pandas as pd
import awkward as ak
import matplotlib.pyplot as plt

columns = [
    "vertex_primary",
    "vertex_secondary",
    "nRecoVtx",
    "nMergedVtx",
    "nSplitVtx",
    "nTrueVtx",
    "nVtxReconstructable",
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "--inputs-tvf", required=True, nargs="+", help="input files truth finder"
)
parser.add_argument(
    "--inputs-gauss", required=True, nargs="+", help="input files gauss finder"
)
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
    "gauss": args.inputs_gauss,
    "truth": args.inputs_tvf,
}
pus = [0, 30, 60, 90, 120, 150, 200]

assert (
    len(pus) == len(args.inputs_tvf) == len(args.inputs_gauss) == len(args.inputs_wot) == len(args.inputs_wt)
), "equal number of inputs required"

fig, axs = plt.subplots(3, 1, figsize=(8, 6), sharex=True)

results = {input_type: [] for input_type in inputs.keys()}

for input_type, inputs_list in inputs.items():
    for input, pu in zip(inputs_list, pus):
        data = ak.to_dataframe(
            uproot.open(input)["vertexing"].arrays(columns, library="ak"),
            how="outer",
        )

        # filter for first primary vertex which is the HS vertex by design
        data = data[(data["vertex_primary"] == 1) & (data["vertex_secondary"] == 0)]

        results[input_type].append(
            {
                "pu": pu,
                "n_true": data["nTrueVtx"].mean(),
                "n_reconstructable": data["nVtxReconstructable"].mean(),
                "n_reco": data["nRecoVtx"].mean(),
                "n_reco_err": data["nRecoVtx"].std(),
                "n_merged": data["nMergedVtx"].mean(),
                "n_merged_err": data["nMergedVtx"].std(),
                "n_split": data["nSplitVtx"].mean(),
                "n_split_err": data["nSplitVtx"].std(),
            }
        )

for input_type in inputs.keys():
    data = pd.DataFrame(results[input_type])

    axs[0].errorbar(
        data["pu"],
        data["n_reco"],
        data["n_reco_err"],
        marker="o",
        linestyle="",
        alpha=0.5,
        label=f"{input_type}",
    )

    axs[1].errorbar(
        data["pu"],
        data["n_merged"],
        marker="o",
        linestyle="",
        alpha=0.5,
        label=f"{input_type}",
    )

    axs[2].errorbar(
        data["pu"],
        data["n_split"],
        marker="o",
        linestyle="",
        alpha=0.5,
        label=f"{input_type}",
    )

axs[0].plot(
    data["pu"],
    data["pu"] + 1,
    linestyle="--",
    color="black",
    label="optimal",
)

axs[1].plot(
    data["pu"],
    np.zeros(data["pu"].shape),
    linestyle="--",
    color="black",
    label="optimal",
)

axs[2].plot(
    data["pu"],
    np.zeros(data["pu"].shape),
    linestyle="--",
    color="black",
    label="optimal",
)

axs[0].grid()
axs[0].legend()
axs[0].set_ylabel("Reconstructed vertices")

axs[1].grid()
axs[1].legend()
axs[1].set_ylabel("Merged vertices")

axs[2].grid()
axs[2].legend()
axs[2].set_xlabel("PU")
axs[2].set_ylabel("Split vertices")

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
