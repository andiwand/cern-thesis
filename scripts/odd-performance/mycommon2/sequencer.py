from pathlib import Path

import acts


def get_sequencer(
    output_files: list[dict[str, str]],
    skip: int,
    events: int,
    threads: int,
    tp: Path,
    decorators: list[object],
) -> acts.examples.Sequencer:
    sequencer = acts.examples.Sequencer(
        skip=skip,
        events=events,
        numThreads=threads,
        trackFpes=False,
        outputDir=tp,
    )
    output_files.append({"file": "timing.csv"})

    for decorator in decorators:
        sequencer.addContextDecorator(decorator)

    return sequencer
