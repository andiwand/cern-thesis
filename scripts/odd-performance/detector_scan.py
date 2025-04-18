#!/usr/bin/env python3

import argparse
import tempfile
from pathlib import Path
import shutil

from mycommon2.detector import get_odd
from mycommon2.rng import get_rng
from mycommon2.sequencer import get_sequencer
from mycommon2.sim import add_my_material_scan_chain


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sim_label")
    parser.add_argument("outdir")
    parser.add_argument("--skip", type=int, required=True, help="Skip number of events")
    parser.add_argument("--events", type=int, required=True, help="Number of events")
    parser.add_argument("--threads", type=int, default=1, help="Number of threads")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    skip = args.skip
    events = args.events

    with tempfile.TemporaryDirectory() as temp:
        run_material_scan(
            threads=args.threads,
            tp=Path(temp),
            sim_label=args.sim_label,
            outdir=outdir,
            skip=skip,
            events=events,
        )

    return 0


def run_material_scan(
    threads: int,
    tp: Path,
    sim_label: str,
    outdir: Path,
    skip: int,
    events: int,
):
    detector, tracking_geometry, decorators, field, digiConfig, seedingSel = get_odd()

    output_files = []

    rng = get_rng(True, None)

    sequencer = get_sequencer(
        output_files=output_files,
        skip=skip,
        events=events,
        threads=threads,
        tp=tp,
        decorators=decorators,
    )

    add_my_material_scan_chain(
        output_files=output_files,
        sequencer=sequencer,
        event_label="geantinos",
        sim_label=sim_label,
        tracking_geometry=tracking_geometry,
        detector=detector,
        rnd=rng,
        tp=tp,
    )

    sequencer.run()
    del sequencer

    outdir.mkdir(parents=True, exist_ok=True)
    for file in output_files:
        source = tp / file["file"]
        destination = outdir / file["move"] if "move" in file else outdir / file["file"]
        assert source.exists(), f"File not found: {source}"
        shutil.copy(source, destination)


if __name__ == "__main__":
    main()
