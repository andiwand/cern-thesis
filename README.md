# Development and performance of track reconstruction software for ATLAS Phase-2 Upgrade and beyond

## Abstract

## Snakemake

Sometimes a rule changes or the scripts which is part of the input, but we belive that the output will be the same. For long jobs we want to skip reprocessing. This can be achieved by cleaning the snakemake cache and touching the relevant output files of these rules.

For example to skip rerunning the simulations jobs for the Acts ODD performance study:
```
rm -rf .snakemake
find data/odd-performance/sim -type f -exec touch {} +
```
