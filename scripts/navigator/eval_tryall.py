# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot
import awkward as ak
import numpy as np
import pandas as pd


base_dir = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input-ref",
    nargs=2,
    type=Path,
    default=[Path(f"{base_dir}/data/navigator/tryall/ref_{mom}GeV") for mom in [1, 10]],
    help="Path to the input file",
)
parser.add_argument(
    "--input-tryall",
    nargs=2,
    type=Path,
    default=[
        Path(f"{base_dir}/data/navigator/tryall/tryall_{mom}GeV") for mom in [1, 10]
    ],
    help="Path to the input file",
)
parser.add_argument(
    "--input-tryalloverstep",
    nargs=2,
    type=Path,
    default=[
        Path(f"{base_dir}/data/navigator/tryall/tryalloverstep_{mom}GeV")
        for mom in [1, 10]
    ],
    help="Path to the input file",
)
args = parser.parse_args()

hits_ref = [
    ak.to_dataframe(uproot.open(f / "hits.root")["hits"].arrays(library="ak"))
    for f in args.input_ref
]
hits_tryall = [
    ak.to_dataframe(uproot.open(f / "hits.root")["hits"].arrays(library="ak"))
    for f in args.input_tryall
]
hits_tryalloverstep = [
    ak.to_dataframe(uproot.open(f / "hits.root")["hits"].arrays(library="ak"))
    for f in args.input_tryalloverstep
]

for mom, ref, tryall, tryalloverstep in zip(
    [1, 10], hits_ref, hits_tryall, hits_tryalloverstep
):
    print(f"momentum: {mom} GeV")
    print(f"ref: {len(ref)}")
    print(f"tryall: {len(tryall)}")
    print(f"tryalloverstep: {len(tryalloverstep)}")
    print()

hits_ref = hits_ref[0]
hits_tryall = hits_tryall[0]
hits_tryalloverstep = hits_tryalloverstep[0]

hits_ref["hit_count"] = 1
hits_tryall["hit_count"] = 1
hits_tryalloverstep["hit_count"] = 1

hit_count_ref = hits_ref[["event_id", "hit_count"]].groupby("event_id").count()
hit_count_tryall = hits_tryall[["event_id", "hit_count"]].groupby("event_id").count()
hit_count_tryalloverstep = (
    hits_tryalloverstep[["event_id", "hit_count"]].groupby("event_id").count()
)
# stack data
hit_count_stacked = pd.concat(
    [
        hit_count_ref.rename(columns={"hit_count": "ref"}),
        hit_count_tryall.rename(columns={"hit_count": "tryall"}),
        hit_count_tryalloverstep.rename(columns={"hit_count": "tryalloverstep"}),
    ],
    axis=1,
)
hit_count_stacked = hit_count_stacked.fillna(0)

# check if all events are present
print(f"event count {len(hit_count_stacked)}")
print(hit_count_stacked.sum())
print()

# find the difference
diff = hit_count_stacked["ref"] - hit_count_stacked["tryall"]
print(f"tryall vs ref: {sum(diff != 0)}")
print(list(hit_count_stacked.index[diff != 0]))
print(list(hit_count_stacked.index[np.abs(diff) > 1]))
diff = hit_count_stacked["ref"] - hit_count_stacked["tryalloverstep"]
print(f"tryalloverstep vs ref: {sum(diff != 0)}")
print(list(hit_count_stacked.index[diff != 0]))
print(list(hit_count_stacked.index[np.abs(diff) > 1]))
diff = hit_count_stacked["tryall"] - hit_count_stacked["tryalloverstep"]
print(f"tryall vs tryalloverstep: {sum(diff != 0)}")
print(list(hit_count_stacked.index[diff != 0]))
print(list(hit_count_stacked.index[np.abs(diff) > 1]))
print()

event = 486
print(hits_ref[hits_ref["event_id"] == event])
print(hits_tryall[hits_tryall["event_id"] == event])
print(hits_tryalloverstep[hits_tryalloverstep["event_id"] == event])
