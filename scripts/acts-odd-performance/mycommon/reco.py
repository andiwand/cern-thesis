from pathlib import Path
from typing import Optional, Union
from collections import namedtuple

import acts
from acts.examples.simulation import (
    addDigitization,
    addParticleSelection,
    ParticleSelectorConfig,
)
from acts.examples.reconstruction import (
    TruthSeedRanges,
    ParticleSmearingSigmas,
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


u = acts.UnitConstants


RecoConfig = namedtuple(
    "RecoCuts",
    ["track_selector_config", "ckf_config", "ambi_config"],
    defaults=[TrackSelectorConfig(), CkfConfig(), AmbiguityResolutionConfig()],
)


def list_reco_labels(config):
    return [create_reco_label(seeding) for seeding in config["seedings"]]


def create_reco_label(seeding):
    return f"{seeding}"


def split_reco_label(reco_label):
    return reco_label


def get_reco_config(event, seeding) -> RecoConfig:
    measurementCounter = acts.TrackSelector.MeasurementCounter()
    # At least 1 hit on the first pixel layers
    measurementCounter.addCounter(
        [
            acts.GeometryIdentifier().setVolume(16).setLayer(16),
            acts.GeometryIdentifier().setVolume(17).setLayer(2),
            acts.GeometryIdentifier().setVolume(18).setLayer(2),
        ],
        1,
    )
    # At least 3 hits in the pixels
    measurementCounter.addCounter(
        [
            acts.GeometryIdentifier().setVolume(16),
            acts.GeometryIdentifier().setVolume(17),
            acts.GeometryIdentifier().setVolume(18),
        ],
        3,
    )

    return RecoConfig(
        track_selector_config=TrackSelectorConfig(
            pt=(0.9 * u.GeV, None),
            absEta=(None, 3.5),
            loc0=(-4.0 * u.mm, 4.0 * u.mm),
            nMeasurementsMin=7,
            nMeasurementsGroupMin=measurementCounter,
            maxHolesAndOutliers=3,
        ),
        ckf_config=CkfConfig(
            chi2CutOffMeasurement=15.0,
            chi2CutOffOutlier=25.0,
            numMeasurementsCutOff=3,
            # TODO for non truth smeared seeding
            # seedDeduplication=True,
            # stayOnSeed=True,
        ),
        ambi_config=AmbiguityResolutionConfig(
            maximumSharedHits=3,
            maximumIterations=100000000,
            nMeasurementsMin=7,
        ),
    )


def addMySeeding(
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
        0 / u.GeV,
        1 * u.ns,
    ]
    initialSigmaPtRel = 0.1
    initialVarInflation = [1e0, 1e0, 1e0, 1e0, 1e0, 1e0]

    particleSmearingSigmas = None
    seedFinderConfigArg = None

    particleHypothesis = acts.ParticleHypothesis.pion

    if seeding_label == "truth_smeared":
        seedingAlgorithm = SeedingAlgorithm.TruthSmeared

        initialSigmas = None
        initialSimgaQoverPCoefficients = None
        initialVarInflation = [1e1, 1e1, 1e1, 1e1, 1e1, 1e1]

        particleSmearingSigmas = ParticleSmearingSigmas(
            d0=20 * u.um,
            d0PtA=30 * u.um,
            d0PtB=0.3 / u.GeV,
            z0=20 * u.um,
            z0PtA=30 * u.um,
            z0PtB=0.3 / u.GeV,
            t0=25 * u.mm,
            phi=0.1 * u.degree,
            theta=0.1 * u.degree,
            ptRel=0.01,
        )

        # note that this will use the true hypothesis
        particleHypothesis = None
    elif seeding_label == "truth_estimated":
        seedingAlgorithm = SeedingAlgorithm.TruthEstimated

        # note that this will use the true hypothesis
        particleHypothesis = None
    elif seeding_label == "default":
        seedingAlgorithm = SeedingAlgorithm.Default

        seedFinderConfigArg = SeedFinderConfigArg(
            r=(33 * u.mm, 200 * u.mm),
            deltaR=(1 * u.mm, 60 * u.mm),
            collisionRegion=(-250 * u.mm, 250 * u.mm),
            z=(-2000 * u.mm, 2000 * u.mm),
            maxSeedsPerSpM=1,
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
        truthSeedRanges=TruthSeedRanges(
            # using something close to 1 to include for sure
            pt=(0.999 * u.GeV, None),
            eta=(-3.0, 3.0),
            nHits=(3, None),
        ),
        particleHypothesis=particleHypothesis,
        particleSmearingSigmas=particleSmearingSigmas,
        seedFinderConfigArg=seedFinderConfigArg,
        initialSigmas=initialSigmas,
        initialSigmaPtRel=initialSigmaPtRel,
        initialVarInflation=initialVarInflation,
        geoSelectionConfigFile=geoSelectionConfigFile,
        outputDirRoot=outputDirRoot,
    )


def add_my_reconstruction_chain(
    output_files: list[dict[str, str]],
    sequencer: acts.examples.Sequencer,
    seeding_label: str,
    tracking_geometry: acts.TrackingGeometry,
    digi_config: str,
    seeding_sel: str,
    reco_config: RecoConfig,
    field: acts.MagneticFieldProvider,
    rnd: acts.examples.RandomNumbers,
    tp: Path,
):
    addDigitization(
        sequencer,
        tracking_geometry,
        field,
        digiConfigFile=digi_config,
        rnd=rnd,
        # outputDirRoot=tp,
    )

    addParticleSelection(
        sequencer,
        ParticleSelectorConfig(
            rho=(0.0, 24 * u.mm),
            absZ=(0.0, 1.0 * u.m),
            eta=(-3.0, 3.0),
            # using something close to 1 to include for sure
            pt=(0.999 * u.GeV, None),
            measurements=(7, None),
            removeNeutral=True,
        ),
        inputParticles="particles_input",
        outputParticles="my_particles_selected",
        inputMeasurementParticlesMap="measurement_particles_map",
    )
    sequencer.addWhiteboardAlias("particles", "particles_input")
    sequencer.addWhiteboardAlias("particles_selected", "my_particles_selected")

    addMySeeding(
        sequencer,
        seeding_label,
        tracking_geometry,
        field,
        rnd=rnd,
        geoSelectionConfigFile=seeding_sel,
        # outputDirRoot=tp,
    )

    addCKFTracks(
        sequencer,
        tracking_geometry,
        field,
        trackSelectorConfig=reco_config.track_selector_config,
        ckfConfig=reco_config.ckf_config,
        outputDirRoot=tp,
    )
    output_files.append({"file": "tracksummary_ckf.root"})
    output_files.append({"file": "performance_ckf.root"})

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
        writeStates=False,
        writeSummary=True,
        writeCKFperformance=True,
    )
    output_files.append({"file": "tracksummary_ambi.root"})
    output_files.append({"file": "performance_ambi.root"})

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
