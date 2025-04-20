#!/usr/bin/env bash

set -e

current_dir=`pwd`
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# param 1 is the list of input rdos; read it and set the input_rdo variable
# param 2 is the number of events; read it and set the n_events variable
# param 3 is the output folder; read it and set the output_folder variable
# param 4 is the number of threads; read it and set the n_threads variable

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <input_rdo_list> <n_events> <output_folder> <n_threads>"
    exit 1
fi

input_rdo=`cat $1 | grep -v "^#"`
n_events=$2
output_dir=$3
n_threads=$4

echo
printf "Input RDOs:\n${input_rdo}\n"
echo "Number of events: ${n_events}"
echo "Output folder: ${output_dir}"
echo "Number of threads: ${n_threads}"
echo

mkdir -p ${output_dir}
mkdir -p ${output_dir}/legacy
mkdir -p ${output_dir}/acts
mkdir -p ${output_dir}/dcube

# run Athena fast legacy

echo "Running Athena fast legacy..."

cd "${output_dir}/legacy"

# use `flags.Common.MsgSuppression=False` to see all messages
Reco_tf.py \
  --inputRDOFile ${input_rdo} \
  --outputAODFile AOD.root \
  --preInclude "InDetConfig.ConfigurationHelpers.OnlyTrackingPreInclude" \
  --preExec "flags.Tracking.doITkFastTracking=True; \
      flags.Tracking.doTruth=True; \
      flags.Tracking.writeExtendedSi_PRDInfo=True; \
      flags.Tracking.doPixelDigitalClustering=True;" \
  --maxEvents ${n_events} \
  --multithreaded True \
  --athenaopts="--threads=${n_threads}"

cd "${current_dir}"

# run Athena fast acts

echo "Running Athena fast acts..."

cd "${output_dir}/acts"

Reco_tf.py \
  --inputRDOFile ${input_rdo} \
  --outputAODFile AOD.root \
  --preInclude "InDetConfig.ConfigurationHelpers.OnlyTrackingPreInclude,ActsConfig.ActsCIFlags.actsFastWorkflowFlags" \
  --preExec "flags.Tracking.doITkFastTracking=True; \
      flags.Tracking.doTruth=True; \
      flags.Tracking.writeExtendedSi_PRDInfo=True; \
      flags.Tracking.doPixelDigitalClustering=True;" \
  --maxEvents ${n_events} \
  --multithreaded True \
  --athenaopts="--threads=${n_threads}"

cd "${current_dir}"

# run IDPVM on fast legacy

echo "Running IDPVM on Athena fast legacy..."

cd "${output_dir}/legacy"

runIDPVM.py \
  --filesInput AOD.root \
  --outputFile idpvm.root \
  --validateExtraTrackCollections "SiSPSeededTracks" \
  --doTechnicalEfficiency \
  --doExpertPlots

cd "${current_dir}"

# run IDPVM on fast acts

echo "Running IDPVM on Athena fast acts..."

cd "${output_dir}/acts"

runIDPVM.py \
  --filesInput AOD.root \
  --outputFile idpvm.root \
  --validateExtraTrackCollections "SiSPSeededTracksActsValidateTracksTrackParticles" \
  --doTechnicalEfficiency \
  --doExpertPlots

cd "${current_dir}"

# run dcube to compare legacy and acts

echo "Running dcube to compare legacy and acts..."

# Compare performance athena vs acts
$ATLAS_LOCAL_ROOT/dcube/current/DCubeClient/python/dcube.py \
  -p -x "${output_dir}/dcube" \
  -c "${script_dir}/dcube.xml" \
  -r "${output_dir}/legacy/idpvm.root" \
  "${output_dir}/acts/idpvm.root"
