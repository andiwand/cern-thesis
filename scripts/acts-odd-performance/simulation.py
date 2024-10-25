#!/usr/bin/env python3

import argparse
import tempfile
from pathlib import Path
import shutil

from mycommon.events import split_event_sim_label
from mycommon.detector import get_odd
from mycommon.rng import get_rng
from mycommon.sequencer import get_sequencer
from mycommon.sim import add_my_simulation_chain


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("event_sim_label")
    parser.add_argument("outdir")
    parser.add_argument("--skip", type=int, required=True, help="Skip number of events")
    parser.add_argument("--events", type=int, required=True, help="Number of events")
    parser.add_argument("--threads", type=int, default=1, help="Number of threads")
    parser.add_argument("--use-event-seed", action="store_true", help="Use event seed")
    args = parser.parse_args()

    event_label, sim_label = split_event_sim_label(args.event_sim_label)

    outdir = Path(args.outdir)
    skip = args.skip
    events = args.events

    with tempfile.TemporaryDirectory() as temp:
        run_simulation(
            threads=args.threads,
            use_event_seed=args.use_event_seed,
            tp=Path(temp),
            event_label=event_label,
            sim_label=sim_label,
            outdir=outdir,
            skip=skip,
            events=events,
        )

    return 0


def run_simulation(
    threads: int,
    use_event_seed: bool,
    tp: Path,
    event_label: str,
    sim_label: str,
    outdir: Path,
    skip: int,
    events: int,
):
    detector, tracking_geometry, decorators, field, digiConfig, seedingSel = get_odd()

    output_files = []

    rng = get_rng(not use_event_seed, event_label)

    sequencer = get_sequencer(
        output_files=output_files,
        skip=skip,
        events=events,
        threads=threads,
        tp=tp,
        decorators=decorators,
    )

    add_my_simulation_chain(
        output_files=output_files,
        sequencer=sequencer,
        event_label=event_label,
        sim_label=sim_label,
        tracking_geometry=tracking_geometry,
        detector=detector,
        field=field,
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
