from pathlib import Path
from typing import Any, Optional, Union

import acts
from acts.examples.simulation import (
    addParticleGun,
    addPythia8,
    addGenParticleSelection,
    MomentumConfig,
    EtaConfig,
    PhiConfig,
    ParticleConfig,
    addFatras,
    addGeant4,
    addSimWriters,
    ParticleSelectorConfig,
    addSimParticleSelection,
)
import acts.examples.geant4

from mycommon.events import get_event_details


u = acts.UnitConstants


def add_my_event_gen(
    output_files: list[dict[str, str]],
    sequencer: acts.examples.Sequencer,
    event_label: str,
    rnd: acts.examples.RandomNumbers,
    outputDirRoot: Optional[Union[Path, str]] = None,
):
    hllhcVtxGen = acts.examples.GaussianVertexGenerator(
        mean=acts.Vector4(0, 0, 0, 0),
        stddev=acts.Vector4(0.0125 * u.mm, 0.0125 * u.mm, 50.0 * u.mm, 180.0 * u.ps),
    )

    event_type, event_details = get_event_details(event_label)

    if event_type == "single_particles":
        particle = event_details["particle"]

        pdg = {
            "mu": acts.PdgParticle.eMuon,
            "pi": acts.PdgParticle.ePionMinus,
            "e": acts.PdgParticle.eElectron,
        }[particle]

        if "pt" in event_details:
            pt = event_details["pt"]
            momentum_config = MomentumConfig(pt, pt, transverse=True)
        elif "pt_range" in event_details:
            pt_min, pt_max = event_details["pt_range"]
            momentum_config = MomentumConfig(pt_min, pt_max, transverse=True)
        else:
            raise ValueError(f"unknown momentum configuration {event_details}")

        addParticleGun(
            sequencer,
            particleConfig=ParticleConfig(num=1, pdg=pdg, randomizeCharge=True),
            momentumConfig=momentum_config,
            etaConfig=EtaConfig(-3.0, 3.0, uniform=True),
            phiConfig=PhiConfig(0.0 * u.degree, 360.0 * u.degree),
            vtxGen=hllhcVtxGen,
            multiplicity=1,
            rnd=rnd,
            outputDirRoot=outputDirRoot,
        )
        output_files.append({"file": "particles.root"})
        output_files.append({"file": "vertices.root"})

        return

    if event_type == "ttbar":
        pu = event_details["pu"]

        addPythia8(
            sequencer,
            rnd=rnd,
            nhard=1,
            npileup=pu,
            beam=acts.PdgParticle.eProton,
            cmsEnergy=14 * u.TeV,
            hardProcess=["Top:qqbar2ttbar = on"],
            pileupProcess=["SoftQCD:all = on"],
            vtxGen=hllhcVtxGen,
            outputDirRoot=outputDirRoot,
        )
        output_files.append({"file": "particles.root"})
        output_files.append({"file": "vertices.root"})

        return

    if event_type == "geantinos":
        vtxGen = acts.examples.GaussianVertexGenerator(
            mean=acts.Vector4(0, 0, 0, 0),
            stddev=acts.Vector4(0, 0, 0, 0),
        )

        addParticleGun(
            sequencer,
            particleConfig=ParticleConfig(
                num=1,
                pdg=acts.PdgParticle.eInvalid,
                charge=0,
                randomizeCharge=False,
                mass=0,
            ),
            momentumConfig=MomentumConfig(1 * u.GeV, 1 * u.GeV, transverse=False),
            etaConfig=EtaConfig(-3.0, 3.0, uniform=True),
            phiConfig=PhiConfig(0.0 * u.degree, 360.0 * u.degree),
            vtxGen=vtxGen,
            multiplicity=1,
            rnd=rnd,
            outputDirRoot=outputDirRoot,
        )
        output_files.append({"file": "particles.root"})
        output_files.append({"file": "vertices.root"})

        return

    raise ValueError(f"unknown event type: {event_type}")


def add_my_simulation(
    output_files: list[dict[str, str]],
    sequencer: acts.examples.Sequencer,
    event_label: str,
    sim_label: str,
    tracking_geometry: acts.TrackingGeometry,
    field: acts.MagneticFieldProvider,
    rnd: acts.examples.RandomNumbers,
    detector: Optional[Any] = None,
    input_particles: str = "particles_generated_selected",
    outputDirCsv: Optional[Union[Path, str]] = None,
    outputDirRoot: Optional[Union[Path, str]] = None,
    logLevel: Optional[acts.logging.Level] = None,
) -> None:
    event_type, event_details = get_event_details(event_label)

    if sim_label == "fatras":
        addFatras(
            s=sequencer,
            trackingGeometry=tracking_geometry,
            field=field,
            rnd=rnd,
            enableInteractions=True,
            inputParticles=input_particles,
            logLevel=logLevel,
        )
    elif sim_label == "geant4":
        # kill secondaries in case of single particles as this overflows the barcode
        kill_secondaries = event_type =="single_particles"

        addGeant4(
            s=sequencer,
            detector=detector,
            trackingGeometry=tracking_geometry,
            field=field,
            rnd=rnd,
            inputParticles=input_particles,
            killVolume=tracking_geometry.highestTrackingVolume,
            killAfterTime=25 * u.ns,
            #killMinEnergy=100 * u.MeV,
            #killMinMomentum=100 * u.MeV,
            killSecondaries=kill_secondaries,
            logLevel=logLevel,
        )
    else:
        raise ValueError(f"unknown simulation label: {sim_label}")

    addSimParticleSelection(
        s=sequencer,
        config=ParticleSelectorConfig(
            pt=(0.1 * u.GeV, None),
            removeNeutral=True,
        ),
        logLevel=logLevel,
    )

    addSimWriters(
        s=sequencer,
        simHits="simhits",
        particlesSimulated="particles_simulated_selected",
        outputDirCsv=outputDirCsv,
        outputDirRoot=outputDirRoot,
        logLevel=logLevel,
    )
    output_files.append({"file": "particles_simulation.root"})
    output_files.append({"file": "hits.root"})


def add_my_material_scan(
    output_files: list[dict[str, str]],
    sequencer: acts.examples.Sequencer,
    sim_label: str,
    tracking_geometry: acts.TrackingGeometry,
    detector: Optional[Any],
    rnd: acts.examples.RandomNumbers,
    input_particles: str = "particles_generated_selected",
    outputDirRoot: Optional[Union[Path, str]] = None,
    logLevel: acts.logging.Level = acts.logging.INFO,
):
    if sim_label == "fatras":
        sequencer.addAlgorithm(
            acts.examples.ParticleTrackParamExtractor(
                level=logLevel,
                inputParticles=input_particles,
                outputTrackParameters="start_parameters",
            )
        )

        nav = acts.Navigator(trackingGeometry=tracking_geometry)
        stepper = acts.StraightLineStepper()
        prop = acts.examples.ConcretePropagator(acts.Propagator(stepper, nav))

        sequencer.addAlgorithm(
            acts.examples.PropagationAlgorithm(
                propagatorImpl=prop,
                level=logLevel,
                energyLoss=False,
                multipleScattering=False,
                sterileLogger=False,
                recordMaterialInteractions=True,
                inputTrackParameters="start_parameters",
                outputSummaryCollection="propagation_summary",
                outputMaterialCollection="material_tracks",
            )
        )

        sequencer.addWriter(
            acts.examples.RootPropagationSummaryWriter(
                level=logLevel,
                inputSummaryCollection="propagation_summary",
                filePath=outputDirRoot / "propagation_summary.root",
            )
        )
        output_files.append({"file": "propagation_summary.root"})

        sequencer.addWriter(
            acts.examples.RootMaterialTrackWriter(
                level=logLevel,
                inputMaterialTracks="material_tracks",
                filePath=outputDirRoot / "material_tracks.root",
                storeSurface=True,
                storeVolume=True,
            )
        )
        output_files.append({"file": "material_tracks.root"})
    elif sim_label == "geant4":
        sequencer.addAlgorithm(
            acts.examples.geant4.Geant4MaterialRecording(
                level=logLevel,
                detector=detector,
                randomNumbers=rnd,
                inputParticles=input_particles,
                outputMaterialTracks="material_tracks",
            )
        )

        sequencer.addWriter(
            acts.examples.RootMaterialTrackWriter(
                prePostStep=True,
                recalculateTotals=True,
                inputMaterialTracks="material_tracks",
                filePath=outputDirRoot / "material_tracks.root",
                level=logLevel,
            )
        )
        output_files.append({"file": "material_tracks.root"})


def add_my_simulation_chain(
    output_files: list[dict[str, str]],
    sequencer: acts.examples.Sequencer,
    event_label: str,
    sim_label: str,
    tracking_geometry: acts.TrackingGeometry,
    detector: acts.Detector,
    field: acts.MagneticFieldProvider,
    rnd: acts.examples.RandomNumbers,
    tp: Path,
):
    add_my_event_gen(
        output_files=output_files,
        sequencer=sequencer,
        event_label=event_label,
        rnd=rnd,
        outputDirRoot=tp,
    )

    addGenParticleSelection(
        sequencer,
        ParticleSelectorConfig(
            # these cuts are necessary because of pythia
            rho=(0.0, 24 * u.mm),
            absZ=(0.0, 1.0 * u.m),
        ),
    )

    add_my_simulation(
        output_files=output_files,
        sequencer=sequencer,
        event_label=event_label,
        sim_label=sim_label,
        tracking_geometry=tracking_geometry,
        field=field,
        rnd=rnd,
        detector=detector,
        outputDirRoot=tp,
    )


def add_my_material_scan_chain(
    output_files: list[dict[str, str]],
    sequencer: acts.examples.Sequencer,
    event_label: str,
    sim_label: str,
    tracking_geometry: acts.TrackingGeometry,
    detector: acts.Detector,
    rnd: acts.examples.RandomNumbers,
    tp: Path,
):
    add_my_event_gen(
        output_files=output_files,
        sequencer=sequencer,
        event_label=event_label,
        rnd=rnd,
        outputDirRoot=tp,
    )

    add_my_material_scan(
        output_files=output_files,
        sequencer=sequencer,
        sim_label=sim_label,
        tracking_geometry=tracking_geometry,
        detector=detector,
        rnd=rnd,
        outputDirRoot=tp,
    )
