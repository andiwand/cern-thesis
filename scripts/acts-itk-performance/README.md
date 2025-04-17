## Samples

- single muons pT=10GeV `mc21_14TeV.900495.PG_single_muonpm_Pt10_etaFlatnp0_43.recon.RDO.e8557_s4422_r16128`

## Get access to `/eos/atlas`

login with cern account

```bash
kinit
```

## Setup Athena

```bash
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase

source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh

asetup Athena,main,latest
```

## Run Athena

something like

```bash
Reco_tf.py \
  --inputRDOFile ${input_rdo} \
  --outputAODFile ${output_aod} \
  --preInclude "InDetConfig.ConfigurationHelpers.OnlyTrackingPreInclude,ActsConfig.ActsCIFlags.actsFastWorkflowFlags" \
  --preExec "flags.Tracking.doTruth=True; \
      flags.Tracking.doITkFastTracking=True; \
      flags.Tracking.writeExtendedSi_PRDInfo=True; \
      flags.Tracking.doStoreTrackSeeds=True; \
      flags.Tracking.ITkActsFastPass.storeTrackSeeds=True; \
      flags.Tracking.doPixelDigitalClustering=True;" \
  --maxEvents ${n_events} \
  --multithreaded True
```

## dcube

config taken from https://gitlab.cern.ch/atlas/athena/-/blob/main/InnerDetector/InDetValidation/InDetPhysValMonitoring/share/dcube_IDPVMPlots_ACTS_CKF_ITk_techeff.xml

## Ref from PF

https://github.com/pbutti/condor_acts

to run the Acts fast chain

```bash
Reco_tf.py \
  --inputRDOFile  ${input_rdo} \
  --outputAODFile ${outFile} \
  --preInclude "InDetConfig.ConfigurationHelpers.OnlyTrackingPreInclude,ActsConfig.ActsCIFlags.actsFastWorkflowFlags" \
  --preExec "flags.Tracking.doTruth=True;  \
      flags.Tracking.doITkFastTracking=True; \
      flags.Tracking.writeExtendedSi_PRDInfo=True; \
      flags.Tracking.doStoreTrackSeeds=True; \
      flags.Tracking.ITkActsFastPass.storeTrackSeeds=True; \
      flags.Tracking.doPixelDigitalClustering=True;" \
  --maxEvents ${n_events} \
  --multithreaded 'True'
```

to run the Legacy fast chain

```bash
Reco_tf.py \
  --inputRDOFile  ${input_rdo} \
  --outputAODFile ${outFile} \
  --preInclude "InDetConfig.ConfigurationHelpers.OnlyTrackingPreInclude" \
  --preExec "flags.Tracking.doITkFastTracking=True; \
      flags.Tracking.doStoreTrackSeeds=True; \
      flags.Tracking.doTruth=True; \
      flags.Tracking.doStoreSiSPSeededTracks=True; flags.Tracking.writeExtendedSi_PRDInfo=True; \
      flags.Tracking.doPixelDigitalClustering=True;" \
  --postExec "from OutputStreamAthenaPool.OutputStreamConfig import addToAOD;toAOD=['xAOD::TrackParticleContainer#SiSPSeedSegments*','xAOD::TrackParticleAuxContainer#SiSPSeedSegments*'];cfg.merge(addToAOD(flags,toAOD))" \
  --maxEvents ${n_events} \
  --multithreaded 'True' 
```

about the RDO stuff

```
1 - r14700 is HS truth only ttbar, while r14701 is Full pileup Truth. SingleLep stands for single lepton Filter, it's a ttbar where a W goes to a lepton. 
2 - single stands indeed for single particle samples. epm should be electron. Then you have muon in muonpm and pion in pionpm. etaFlat stands for flat eta distribution and pT10 for fixed pt at 10GeV. 
3 - the e-tag is how the event was generated (EVNT files), s-tag how the detector interaction was simulated (EVNT->HITS) and r-tag how was digitized (HITS->RDO) (and sometimes reconstructed (RDO->AOD)) 

To check what the tags do, i.e. for example how I make sure that r14701 is full pileup truth you do something like
- `setupATLAS`; `asetup main,latest,Athena` or something like that
- `lsetup rucio` to get the voms proxy
- (i think it gives the command to get the proxy i never remember)
- then `GetTfCommand.py --AMI=r14701` and tells you exactly how it was produced from the AMI tag
```
