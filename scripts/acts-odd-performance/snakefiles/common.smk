from mycommon.events import list_event_sim_labels


def get_scan_threads(wildcards):
    return 1

def get_sim_threads(wildcards):
    return 1

def get_number_of_events(wildcards):
    event_sim_label = wildcards["event_sim_label"]
    if event_sim_label in config["events"]:
        return config["events"][event_sim_label]["number_of_events"]
    return config["events"]["others"]["number_of_events"]


configfile: "scripts/acts-odd-performance/config.yaml"


SIM_OUTPUTS = ["particles.root", "hits.root"]
EVENT_SIM_LABELS = list_event_sim_labels(config)
