#!/usr/bin/env python3

import argparse
from pathlib import Path
import tempfile
import shutil
from typing import Optional

import acts

from mycommon.events import split_event_sim_label
from mycommon.detector import get_odd
from mycommon.rng import get_rng
from mycommon.sequencer import get_sequencer
from mycommon.sim import add_my_simulation_chain
from mycommon.reco import split_reco_label, get_reco_config, add_my_reconstruction_chain


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("event_sim_label")
    parser.add_argument("reco_label")
    parser.add_argument("outdir")
    parser.add_argument("--simdir", type=str, help="Simulation input directory")
    parser.add_argument("--skip", type=int, required=True, help="Skip number of events")
    parser.add_argument("--events", type=int, required=True, help="Number of events")
    parser.add_argument("--threads", type=int, default=1, help="Number of threads")
    parser.add_argument("--use-event-seed", action="store_true", help="Use event seed")
    args = parser.parse_args()

    event_label, simulation_label = split_event_sim_label(args.event_sim_label)
    seeding_label = split_reco_label(args.reco_label)

    simdir = None if args.simdir is None else Path(args.simdir)
    outdir = Path(args.outdir)
    skip = args.skip
    events = args.events

    with tempfile.TemporaryDirectory() as temp:
        run_reconstruction(
            threads=args.threads,
            use_event_seed=args.use_event_seed,
            tp=Path(temp),
            event_label=event_label,
            simulation_label=simulation_label,
            seeding_label=seeding_label,
            simdir=simdir,
            outdir=outdir,
            skip=skip,
            events=events,
        )


def run_reconstruction(
    threads: int,
    use_event_seed: bool,
    tp: Path,
    event_label: str,
    simulation_label: str,
    seeding_label: str,
    simdir: Optional[Path],
    outdir: Path,
    skip: int,
    events: int,
):
    detector, tracking_geometry, decorators, field, digi_config, seeding_sel = get_odd()

    reco_config = get_reco_config(event_label, seeding_label)

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

    if simdir is not None:
        sequencer.addReader(
            acts.examples.RootParticleReader(
                level=acts.logging.WARNING,
                outputParticles="particles_input",
                filePath=simdir / "particles.root",
            )
        )
        sequencer.addReader(
            acts.examples.RootVertexReader(
                level=acts.logging.WARNING,
                outputVertices="vertices_input",
                filePath=simdir / "vertices.root",
            )
        )
        sequencer.addReader(
            acts.examples.RootSimHitReader(
                level=acts.logging.WARNING,
                outputSimHits="simhits",
                treeName="hits",
                filePath=simdir / "hits.root",
            )
        )
    else:
        add_my_simulation_chain(
            output_files=[],  # not outputting the simulation files
            sequencer=sequencer,
            event_label=event_label,
            simulation_label=simulation_label,
            tracking_geometry=tracking_geometry,
            detector=detector,
            field=field,
            rnd=rng,
            tp=None,
        )

    add_my_reconstruction_chain(
        output_files=output_files,
        sequencer=sequencer,
        seeding_label=seeding_label,
        tracking_geometry=tracking_geometry,
        digi_config=digi_config,
        seeding_sel=seeding_sel,
        reco_config=reco_config,
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
