from mycommon.config import (
    list_event_sim_labels,
    list_event_sim_reco_labels,
    create_event_sim_label,
    split_event_sim_label,
    split_event_sim_reco_label,
    get_event_details,
    get_number_of_events as get_number_of_events_,
    get_events_per_slice as get_events_per_slice_,
    get_skip_events as get_skip_events_,
)


def get_scan_threads(wildcards):
    return 1

def get_sim_threads(wildcards):
    return 1

def get_reco_threads(wildcards):
    return 1

def get_sim_mem_mb(wildcards):
    event_sim_label = wildcards.event_sim_label
    event, sim = split_event_sim_label(event_sim_label)
    event_type, _ = get_event_details(event)
    if sim == "fatras":
        return 100
    if sim == "geant4":
        if event_type == "single_particles":
            return 1000
        if event_type == "ttbar":
            return 15000
    raise ValueError(f"Unknown event sim label: {event_sim_label}")

def get_reco_mem_mb(wildcards):
    return 500

def get_number_of_events(wildcards):
    if hasattr(wildcards, "event_sim_label"):
        event_sim_label = wildcards.event_sim_label
        return get_number_of_events_(config, event_sim_label)
    if hasattr(wildcards, "event_sim_reco_label"):
        event_sim_reco_label = wildcards.event_sim_reco_label
        event_label, sim_label, _ = split_event_sim_reco_label(event_sim_reco_label)
        event_sim_label = create_event_sim_label(event_label, sim_label)
        return get_number_of_events_(config, event_sim_label)
    raise ValueError("Unknown wildcards")

def get_events_per_slice(wildcards):
    event_sim_label = wildcards.event_sim_label
    return get_events_per_slice_(config, event_sim_label)

def get_skip_events(wildcards):
    event_sim_label = wildcards.event_sim_label
    return get_skip_events_(config, event_sim_label)

def get_event_sim_label(wildcards):
    event_sim_reco_label = wildcards.event_sim_reco_label
    event_label, sim_label, reco_label = split_event_sim_reco_label(event_sim_reco_label)
    return create_event_sim_label(event_label, sim_label)


configfile: "scripts/acts-odd-performance/config.yaml"


EVENT_SIM_LABELS = list_event_sim_labels(config)
EVENT_SIM_RECO_LABELS = list_event_sim_reco_labels(config)
SIM_OUTPUTS = ["particles.root", "vertices.root", "particles_simulation.root", "hits.root"]
RECO_OUTPUTS = ["performance_finding_ckf.root", "performance_fitting_ckf.root"]


wildcard_constraints:
    skip="[0-9]+",
    events="[0-9]+",
    event_sim_label="|".join(EVENT_SIM_LABELS),
    event_sim_reco_label="|".join(EVENT_SIM_RECO_LABELS),
    sim_output="|".join(SIM_OUTPUTS),
    reco_output="|".join(RECO_OUTPUTS)
