from mycommon.events import (
    list_event_sim_labels,
    split_event_sim_label,
    get_number_of_events as get_number_of_events_,
    get_events_per_slice as get_events_per_slice_,
    get_skip_events as get_skip_events_,
)


def get_scan_threads(wildcards):
    return 1

def get_sim_threads(wildcards):
    return 1

def get_number_of_events(wildcards):
    event_sim_label = wildcards["event_sim_label"]
    return get_number_of_events_(config, event_sim_label)

def get_events_per_slice(wildcards):
    event_sim_label = wildcards["event_sim_label"]
    return get_events_per_slice_(config, event_sim_label)

def get_skip_events(wildcards):
    event_sim_label = wildcards["event_sim_label"]
    return get_skip_events_(config, event_sim_label)


configfile: "scripts/acts-odd-performance/config.yaml"


SIM_OUTPUTS = ["particles.root", "vertices.root", "particles_simulation.root", "hits.root"]
EVENT_SIM_LABELS = list_event_sim_labels(config)


wildcard_constraints:
    skip="[0-9]+",
    events="[0-9]+",
    sim_output="|".join(SIM_OUTPUTS),
    event_sim_label="|".join(EVENT_SIM_LABELS)
