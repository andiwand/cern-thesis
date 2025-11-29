# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    nargs=3,
    type=Path,
    default=[
        f"{base_dir}/data/stepper/adaptive-step-size/sympy-10m-{mom}GeV.csv"
        for mom in [1, 10, 100]
    ],
    help="Path to the input file",
)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/stepper/adaptive_step_size_error.pdf",
    help="Path to output file",
)
parser.add_argument("--bins", type=int, default=30, help="Number of bins")
parser.add_argument("--e-range", nargs=2, default=[2, 300], help="Energy range in GeV")
parser.add_argument(
    "--min-p-out", type=float, default=2, help="Minimum output momentum"
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

fig, axs = plt.subplots(
    2, 1, figsize=(8, 4), sharex=True, sharey=False, gridspec_kw={"hspace": 0.0}
)

datas = [pd.read_csv(input) for input in args.input]

# axs[0].set_xlabel("Step number")
axs[0].set_ylabel("Estimated error [mm]")

axs[1].set_xlabel("Step number")
axs[1].set_ylabel("Step size [mm]")

xrange = [datas[0]["nstep"].min() - 5, datas[0]["nstep"].max() + 5]
accuracy = 1e-4
axs[0].fill_between(
    xrange,
    accuracy * 1 / 4,
    accuracy * 4,
    color="gray",
    alpha=0.5,
    label="Accuracy limit",
)
axs[0].hlines(accuracy, *xrange, color="gray", linestyle="--")

for data, mom in zip(datas, [1, 10, 100]):
    axs[0].plot(data["nstep"], data["error"], label=f"$p_T$={mom} GeV")
    axs[1].plot(data["nstep"], data["size"], label=f"$p_T$={mom} GeV")

axs[0].set_xlim(xrange)
# axs[0].set_xscale("log")
axs[0].set_yscale("log")

axs[1].set_yscale("log")

axs[0].legend(loc="lower right")

fig.tight_layout()

if args.output is not None:
    fig.savefig(args.output)

if args.output is None or args.show:
    plt.show()
