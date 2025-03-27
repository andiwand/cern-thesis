import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import ROOT

from mycommon.root import TEfficiency


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("mu1GeV_finding_perf", type=Path)
parser.add_argument("mu10GeV_finding_perf", type=Path)
parser.add_argument("mu100GeV_finding_perf", type=Path)
parser.add_argument("--mu1GeV-seeding-perf", type=Path)
parser.add_argument("--mu10GeV-seeding-perf", type=Path)
parser.add_argument("--mu100GeV-seeding-perf", type=Path)
parser.add_argument(
    "--output",
    type=Path,
    default=f"{base_dir}/plots/acts-odd-performance/finding_efficiency_mu.pdf",
    help="Path to output file",
)
parser.add_argument("--show", action="store_true", help="Show plot")
args = parser.parse_args()

pt = [1, 10, 100]
finding_perf = [args.mu1GeV_finding_perf, args.mu10GeV_finding_perf, args.mu100GeV_finding_perf]
finding_perf = [ROOT.TFile.Open(p.absolute().as_posix()) for p in finding_perf]
seeding_perf = [args.mu1GeV_seeding_perf, args.mu10GeV_seeding_perf, args.mu100GeV_seeding_perf]
seeding_perf = [ROOT.TFile.Open(p.absolute().as_posix()) if p is not None else None for p in seeding_perf]

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

ax.set_xlabel(r"$\eta$")
ax.set_ylabel("Efficiency")

ax.hlines(1, -3, 3, linestyles="--", color="gray")

for i, pt, fperf, sperf in zip(range(3), pt, finding_perf, seeding_perf):
    eff_vs_eta = TEfficiency(fperf.Get("trackeff_vs_eta"))
    eff_vs_eta.errorbar(ax, fmt="o", label=f"{pt} GeV", color=f"C{i}")

    if sperf is not None:
        eff_vs_eta = TEfficiency(sperf.Get("trackeff_vs_eta"))
        eff_vs_eta.errorbar(ax, fmt="o", label=f"{pt} GeV (seeding)", color=f"C{i}", alpha=0.5)

ax.legend()

if args.output is not None:
    fig.savefig(args.output, bbox_inches="tight")

if args.output is None or args.show:
    plt.show()
