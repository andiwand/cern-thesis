import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT

from mycommon.root import TEfficiency


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("finding_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

finding_perf = ROOT.TFile.Open(args.finding_perf.absolute().as_posix())

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Duplicates")

dupl_vs_eta = TEfficiency(finding_perf.Get("nDuplicated_vs_eta"))
dupl_vs_eta.errorbar(ax, fmt="o")

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
