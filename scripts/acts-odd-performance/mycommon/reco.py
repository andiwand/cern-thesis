from pathlib import Path
from typing import Optional, Union
from collections import namedtuple

import acts
from acts.examples.simulation import (
    addSimParticleSelection,
    addDigitization,
    addDigiParticleSelection,
    ParticleSelectorConfig,
)
from acts.examples.reconstruction import (
    TrackSmearingSigmas,
    TruthEstimatedSeedingAlgorithmConfigArg,
    SeedingAlgorithm,
    SeedFinderConfigArg,
    addSeeding,
    TrackSelectorConfig,
    CkfConfig,
    AmbiguityResolutionConfig,
    addTrackWriters,
    addCKFTracks,
    addAmbiguityResolution,
    VertexFinder,
    addVertexFitting,
)
from mycommon.config import split_reco_label, get_event_details


u = acts.UnitConstants


RecoConfig = namedtuple(
    "RecoCuts",
    ["track_selector_config", "ckf_config", "ambi_config"],
    defaults=[TrackSelectorConfig(), CkfConfig(), AmbiguityResolutionConfig()],
)


def make_geoid(vol=None, lay=None):
        geoid = acts.GeometryIdentifier()
        if vol is not None:
            geoid.volume = vol
        if lay is not None:
            geoid.layer = lay
        return geoid


def get_reco_config(event_label, sim_label, reco_label) -> RecoConfig:
    pileup, seeding = split_reco_label(reco_label)

    measurementCounter = acts.TrackSelector.MeasurementCounter()
    # At least 1 hit on the first pixel layers
    measurementCounter.addCounter(
        [
            make_geoid(16, 16),
            make_geoid(17, 2),
            make_geoid(18, 2),
        ],
        1,
    )
    # At least 3 hits in the pixels
    measurementCounter.addCounter(
        [
            make_geoid(16),
            make_geoid(17),
            make_geoid(18),
        ],
        3,
    )

    return RecoConfig(
        track_selector_config=TrackSelectorConfig(
            pt=(0.7 * u.GeV, None),
            absEta=(None, 3.5),
            nMeasurementsMin=6,
            #nMeasurementsGroupMin=measurementCounter,
            maxHolesAndOutliers=3,
        ),
        ckf_config=CkfConfig(
            chi2CutOffMeasurement=15.0,
            chi2CutOffOutlier=25.0,
            numMeasurementsCutOff=1,
            seedDeduplication=seeding != "truth-smeared",
            stayOnSeed=seeding != "truth-smeared",
        ),
        ambi_config=AmbiguityResolutionConfig(
            maximumSharedHits=3,
            maximumIterations=100000,
            nMeasurementsMin=6,
        ),
    )


def add_my_seeding(
    sequencer: acts.examples.Sequencer,
    seeding_label: str,
    trackingGeometry: acts.TrackingGeometry,
    field: acts.MagneticFieldProvider,
    rnd: acts.examples.RandomNumbers,
    geoSelectionConfigFile: str,
    outputDirRoot: Optional[Union[Path, str]] = None,
):
    initialSigmas = [
        1 * u.mm,
        1 * u.mm,
        1 * u.degree,
        1 * u.degree,
        0.1 / u.GeV,
        1 * u.ns,
    ]
    initialSigmaPtRel = 0.1
    initialVarInflation = [1e0, 1e0, 1e0, 1e0, 1e0, 1e0]

    trackSmearingSigmas = None
    truthEstimatedSeedingAlgorithmConfigArg = None
    seedFinderConfigArg = None

    particleHypothesis = acts.ParticleHypothesis.pion

    if seeding_label == "truth-smeared":
        seedingAlgorithm = SeedingAlgorithm.TruthSmeared

        trackSmearingSigmas = TrackSmearingSigmas(
            loc0=0 * u.um,
            loc0PtA=0 * u.um,
            loc0PtB=0 / u.GeV,
            loc1=0 * u.um,
            loc1PtA=0 * u.um,
            loc1PtB=0 / u.GeV,
            time=0 * u.mm,
            phi=0 * u.degree,
            theta=0 * u.degree,
            ptRel=0,
        )

        # note that this will use the true hypothesis
        particleHypothesis = None
    elif seeding_label == "truth-estimated":
        seedingAlgorithm = SeedingAlgorithm.TruthEstimated

        truthEstimatedSeedingAlgorithmConfigArg = TruthEstimatedSeedingAlgorithmConfigArg(
            deltaR=(1 * u.mm, 300 * u.mm),
        )

        # note that this will use the true hypothesis
        particleHypothesis = None
    elif seeding_label == "triplet":
        seedingAlgorithm = SeedingAlgorithm.Default

        seedFinderConfigArg = SeedFinderConfigArg(
            r=(33 * u.mm, 200 * u.mm),
            # kills efficiency at |eta|~2
            deltaR=(1 * u.mm, 300 * u.mm),
            collisionRegion=(-250 * u.mm, 250 * u.mm),
            z=(-2000 * u.mm, 2000 * u.mm),
            maxSeedsPerSpM=3,
            sigmaScattering=5,
            radLengthPerSeed=0.1,
            minPt=0.5 * u.GeV,
            impactMax=3 * u.mm,
        )

        particleHypothesis = acts.ParticleHypothesis.pion
    else:
        raise ValueError(f"unknown seeding label: {seeding_label}")

    addSeeding(
        sequencer,
        trackingGeometry,
        field,
        rnd=rnd,
        seedingAlgorithm=seedingAlgorithm,
        trackSmearingSigmas=trackSmearingSigmas,
        particleHypothesis=particleHypothesis,
        seedFinderConfigArg=seedFinderConfigArg,
        truthEstimatedSeedingAlgorithmConfigArg=truthEstimatedSeedingAlgorithmConfigArg,
        initialSigmas=initialSigmas,
        initialSigmaPtRel=initialSigmaPtRel,
        initialVarInflation=initialVarInflation,
        geoSelectionConfigFile=geoSelectionConfigFile,
        outputDirRoot=outputDirRoot,
    )


def add_my_reconstruction_chain(
    output_files: list[dict[str, str]],
    sequencer: acts.examples.Sequencer,
    reco_label: str,
    event_label: str,
    tracking_geometry: acts.TrackingGeometry,
    digi_config: str,
    seeding_sel: str,
    reco_config: RecoConfig,
    field: acts.MagneticFieldProvider,
    rnd: acts.examples.RandomNumbers,
    tp: Path,
):
    pileup, seeding_label = split_reco_label(reco_label)
    event_type, _ = get_event_details(event_label)

    addSimParticleSelection(
        sequencer,
        ParticleSelectorConfig(
            primaryVertexId=(1, 2 + pileup),
        ),
        logLevel=acts.logging.INFO,
    )
    sequencer.addAlgorithm(
        acts.examples.VertexSelector(
            level=acts.logging.INFO,
            inputVertices="vertices_generated",
            outputVertices="vertices_selected",
            minPrimaryVertexId=1,
            maxPrimaryVertexId=2 + pileup,
        )
    )
    sequencer.addAlgorithm(
        acts.examples.HitSelector(
            level=acts.logging.INFO,
            inputHits="simhits",
            inputParticlesSelected="particles_simulated_selected",
            outputHits="simhits_selected",
        ),
    )

    addDigitization(
        sequencer,
        tracking_geometry,
        field,
        digiConfigFile=digi_config,
        rnd=rnd,
        # outputDirRoot=tp,
    )

    measurementCounter = acts.examples.ParticleSelector.MeasurementCounter()
    # At least 3 hits in the pixels
    measurementCounter.addCounter(
        [
            make_geoid(16),
            make_geoid(17),
            make_geoid(18),
        ],
        3,
    )

    addDigiParticleSelection(
        sequencer,
        ParticleSelectorConfig(
            rho=(0.0, 24 * u.mm),
            absZ=(0.0, 1.0 * u.m),
            eta=(-3.0, 3.0),
            # using something close to 1 to include for sure
            pt=(0.999 * u.GeV, None),
            measurements=(6, None),
            removeNeutral=True,
            removeSecondaries=event_type == "single_particles",
            nMeasurementsGroupMin=measurementCounter,
        ),
    )

    add_my_seeding(
        sequencer,
        seeding_label,
        tracking_geometry,
        field,
        rnd=rnd,
        geoSelectionConfigFile=seeding_sel,
        outputDirRoot=tp,
    )
    if seeding_label != "truth-smeared":
        output_files.append({"file": "performance_seeding.root"})

    addCKFTracks(
        sequencer,
        tracking_geometry,
        field,
        trackSelectorConfig=reco_config.track_selector_config,
        ckfConfig=reco_config.ckf_config,
        twoWay=True,
        outputDirRoot=tp,
        #logLevel=acts.logging.VERBOSE,
    )
    output_files.append({"file": "performance_finding_ckf.root"})
    output_files.append({"file": "performance_fitting_ckf.root"})

    if event_type == "ttbar":
        addAmbiguityResolution(
            sequencer,
            config=reco_config.ambi_config,
            # outputDirRoot=tp,
        )
        addTrackWriters(
            sequencer,
            name="ambi",
            tracks="tracks",
            outputDirRoot=tp,
            writeSummary=False,
            writeStates=False,
            writeFitterPerformance=True,
            writeFinderPerformance=True,
            writeCovMat=False,
        )
        output_files.append({"file": "performance_finding_ambi.root"})

        sequencer.addAlgorithm(
            acts.examples.TracksToParameters(
                level=acts.logging.INFO,
                inputTracks="tracks",
                outputTrackParameters="track_parameters",
            )
        )

        addVertexFitting(
            sequencer,
            field,
            trackParameters="track_parameters",
            outputProtoVertices="tvf_protovertices",
            outputVertices="tvf_fittedVertices",
            vertexFinder=VertexFinder.Truth,
            outputDirRoot=tp / "tvf",
        )
        output_files.append(
            {
                "file": "tvf/performance_vertexing.root",
                "move": "performance_tvf.root",
            }
        )

        addVertexFitting(
            sequencer,
            field,
            trackParameters="track_parameters",
            outputProtoVertices="ivf_protovertices",
            outputVertices="ivf_fittedVertices",
            vertexFinder=VertexFinder.Iterative,
            outputDirRoot=tp / "ivf",
        )
        output_files.append(
            {
                "file": "ivf/performance_vertexing.root",
                "move": "performance_ivf.root",
            }
        )

        addVertexFitting(
            sequencer,
            field,
            trackParameters="track_parameters",
            outputProtoVertices="amvf_gauss_protovertices",
            outputVertices="amvf_gauss_fittedVertices",
            seeder=acts.VertexSeedFinder.GaussianSeeder,
            useTime=False,
            vertexFinder=VertexFinder.AMVF,
            outputDirRoot=tp / "amvf_gauss",
        )
        output_files.append(
            {
                "file": "amvf_gauss/performance_vertexing.root",
                "move": "performance_amvf_gauss.root",
            }
        )

        addVertexFitting(
            sequencer,
            field,
            trackParameters="track_parameters",
            outputProtoVertices="amvf_truth_notime_protovertices",
            outputVertices="amvf_truth_notime_fittedVertices",
            seeder=acts.VertexSeedFinder.TruthSeeder,
            useTime=False,
            vertexFinder=VertexFinder.AMVF,
            outputDirRoot=tp / "amvf_truth_notime",
        )
        output_files.append(
            {
                "file": "amvf_truth_notime/performance_vertexing.root",
                "move": "performance_amvf_truth_notime.root",
            }
        )

        addVertexFitting(
            sequencer,
            field,
            trackParameters="track_parameters",
            outputProtoVertices="amvf_truth_time_protovertices",
            outputVertices="amvf_truth_time_fittedVertices",
            seeder=acts.VertexSeedFinder.TruthSeeder,
            useTime=True,
            vertexFinder=VertexFinder.AMVF,
            outputDirRoot=tp / "amvf_truth_time",
        )
        output_files.append(
            {
                "file": "amvf_truth_time/performance_vertexing.root",
                "move": "performance_amvf_truth_time.root",
            }
        )
