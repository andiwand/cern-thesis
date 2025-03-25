import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT

from mycommon.root import TEfficiency


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("--triplet-perf", type=Path, required=True)
parser.add_argument("--truth-perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/acts-odd-performance/seeding_efficiency.pdf",
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()


triplet_perf = ROOT.TFile.Open(args.triplet_perf.absolute().as_posix())
if args.truth_perf is not None:
    truth_perf = ROOT.TFile.Open(args.truth_perf.absolute().as_posix())

fig, ax = plt.subplots(1, 2, figsize=(8, 4))

ax[0].set_xlabel(r"$\eta$")
ax[0].set_ylabel("Efficiency")

eff_vs_eta_triplet = TEfficiency(triplet_perf.Get("trackeff_vs_eta"))
eff_vs_eta_triplet.errorbar(ax[0], fmt="o", label="Triplet")

if args.truth_perf is not None:
    eff_vs_eta_truth = TEfficiency(truth_perf.Get("trackeff_vs_eta"))
    eff_vs_eta_truth.errorbar(ax[0], fmt="o", label="Truth")

ax[0].legend()

ax[1].set_xlabel(r"$\eta$")
ax[1].set_ylabel("Duplication rate")

dup_vs_eta_triplet = TEfficiency(triplet_perf.Get("duplicationRate_vs_eta"))
dup_vs_eta_triplet.errorbar(ax[1], fmt="o", label="Triplet")

if args.truth_perf is not None:
    dup_vs_eta_truth = TEfficiency(truth_perf.Get("duplicationRate_vs_eta"))
    dup_vs_eta_truth.errorbar(ax[1], fmt="o", label="Truth")

ax[1].legend()

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
