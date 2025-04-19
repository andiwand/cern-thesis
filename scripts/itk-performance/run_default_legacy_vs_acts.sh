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
mkdir -p ${output_dir}/acts_modified
mkdir -p ${output_dir}/dcube_legacy_acts
mkdir -p ${output_dir}/dcube_legacy_acts_modified

export ATHENA_CORE_NUMBER=${n_threads}

# run Athena default legacy

echo "Running Athena default legacy..."

cd "${output_dir}/legacy"

# use `flags.Common.MsgSuppression=False` to see all messages
Reco_tf.py \
  --inputRDOFile ${input_rdo} \
  --outputAODFile AOD.root \
  --preInclude "InDetConfig.ConfigurationHelpers.OnlyTrackingPreInclude" \
  --preExec "flags.Tracking.doTruth=True; \
      flags.Tracking.writeExtendedSi_PRDInfo=True; \
      flags.Tracking.doPixelDigitalClustering=True;" \
  --maxEvents ${n_events} \
  --multithreaded True \
  --perfmon fullmonmt

cd "${current_dir}"

# run Athena default acts

echo "Running Athena default acts..."

cd "${output_dir}/acts"

Reco_tf.py \
  --inputRDOFile ${input_rdo} \
  --outputAODFile AOD.root \
  --preInclude "InDetConfig.ConfigurationHelpers.OnlyTrackingPreInclude,ActsConfig.ActsCIFlags.actsWorkflowFlags" \
  --preExec "flags.Tracking.doTruth=True; \
      flags.Tracking.writeExtendedSi_PRDInfo=True; \
      flags.Tracking.doPixelDigitalClustering=True;" \
  --maxEvents ${n_events} \
  --multithreaded True \
  --perfmon fullmonmt

cd "${current_dir}"

# run Athena default acts modified

echo "Running Athena default acts modified..."

cd "${output_dir}/acts_modified"

Reco_tf.py \
  --inputRDOFile ${input_rdo} \
  --outputAODFile AOD.root \
  --preInclude "InDetConfig.ConfigurationHelpers.OnlyTrackingPreInclude,ActsConfig.ActsCIFlags.actsWorkflowFlags" \
  --preExec "flags.Tracking.doTruth=True; \
      flags.Tracking.writeExtendedSi_PRDInfo=True; \
      flags.Tracking.doPixelDigitalClustering=True;" \
  --postExec "ckf=cfg.getEventAlgo('ActsTrackFindingAlg');ckf.chi2CutOff=[100];ckf.chi2OutlierCutOff=[100]" \
  --maxEvents ${n_events} \
  --multithreaded True \
  --perfmon fullmonmt

cd "${current_dir}"

# run IDPVM on default legacy

echo "Running IDPVM on Athena default legacy..."

cd "${output_dir}/legacy"

runIDPVM.py \
  --filesInput AOD.root \
  --outputFile idpvm.root \
  --validateExtraTrackCollections "SiSPSeededTracks" \
  --doTechnicalEfficiency \
  --doExpertPlots

cd "${current_dir}"

# run IDPVM on default acts

echo "Running IDPVM on Athena default acts..."

cd "${output_dir}/acts"

runIDPVM.py \
  --filesInput AOD.root \
  --outputFile idpvm.root \
  --validateExtraTrackCollections "SiSPSeededTracksActsValidateTracksTrackParticles" \
  --doTechnicalEfficiency \
  --doExpertPlots

cd "${current_dir}"

# run IDPVM on default acts modified

echo "Running IDPVM on Athena default acts modified..."

cd "${output_dir}/acts_modified"

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
  -p -x "${output_dir}/dcube_legacy_acts" \
  -c "${script_dir}/dcube_IDPVMPlots_ACTS_CKF_ITk_techeff.xml" \
  -r "${output_dir}/legacy/idpvm.root" \
  "${output_dir}/acts/idpvm.root"

# run dcube to compare legacy and acts modified

echo "Running dcube to compare legacy and acts modified..."

# Compare performance athena vs acts modified
$ATLAS_LOCAL_ROOT/dcube/current/DCubeClient/python/dcube.py \
  -p -x "${output_dir}/dcube_legacy_acts_modified" \
  -c "${script_dir}/dcube_IDPVMPlots_ACTS_CKF_ITk_techeff.xml" \
  -r "${output_dir}/legacy/idpvm.root" \
  "${output_dir}/acts_modified/idpvm.root"
