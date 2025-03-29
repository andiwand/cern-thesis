import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT

from mycommon.root import TEfficiency


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("mu_seeding_perf", type=Path)
parser.add_argument("pi_seeding_perf", type=Path)
parser.add_argument("e_seeding_perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

ptypes = ["mu", "pi", "e"]
seeding_perf = [args.mu_seeding_perf, args.pi_seeding_perf, args.e_seeding_perf]
seeding_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in seeding_perf]

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Efficiency")

ax.hlines(1, -3, 3, linestyles="--", color="gray")

for ptype, perf in zip(ptypes, seeding_perf):
    eff_vs_eta = TEfficiency(perf.Get("trackeff_vs_eta"))
    eff_vs_eta.errorbar(ax, fmt="o", label=f"{ptype}")

ax.legend()

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
