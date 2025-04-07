## Run material composition

Taken from https://gitlab.cern.ch/acts/OpenDataDetector

```
ActsAnalysisMaterialComposition -i $input -o $output --config ci/composition_config.json -s
```

eg

```
~/cern/build/acts/acts/dev3/bin/ActsAnalysisMaterialComposition -i data/acts-odd-performance/scan/geant4/material_tracks.root -o data/acts-odd-performance/scan/geant4/material_composition.root --config scripts/acts-introduction/odd_composition_config.json -s 
```
