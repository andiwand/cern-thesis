import re
import itertools


def list_event_labels(config):
    return (
        [
            f"1{particle}-pt{pt}GeV"
            for particle, pt in itertools.product(
                ["mu", "pi", "e"], config["events"]["single_particles"]["pts"]
            )
        ]
        + [f"1{particle}-pt1-100GeV" for particle in ["mu", "pi", "e"]]
        + [f"ttbar-pu{config["events"]["ttbar"]["pileup"]}"]
    )


def list_sim_labels(config):
    return config["simulation"]["algorithms"]


def list_event_sim_labels(config):
    return [
        create_event_sim_label(event, simulation)
        for event, simulation in itertools.product(
            list_event_labels(config), list_sim_labels(config)
        )
    ]


def list_reco_labels(config):
    return [create_reco_label(seeding) for seeding in config["reconstruction"]["seeding"]]


def create_event_sim_label(event_label, sim_label):
    return f"{event_label}_{sim_label}"


def create_reco_label(seeding):
    return f"{seeding}"


def split_event_sim_label(event_sim_label):
    m = re.match(r"^(.+)_(.+?)$", event_sim_label)
    if m:
        return m.group(1), m.group(2)
    raise ValueError(f"unknown event label {event_sim_label}")


def split_reco_label(reco_label):
    return reco_label


def get_number_of_events(config, event_sim_label):
    event, _ = split_event_sim_label(event_sim_label)
    if event.startswith("ttbar"):
        return config["events"]["ttbar"]["number_of_events"]
    return config["events"]["single_particles"]["number_of_events"]


def get_events_per_slice(config, event_sim_label):
    event, _ = split_event_sim_label(event_sim_label)
    if event.startswith("ttbar"):
        return config["events"]["ttbar"]["events_per_slice"]
    return config["events"]["single_particles"]["events_per_slice"]


def get_skip_events(config, event_sim_label):
    total = get_number_of_events(config, event_sim_label)
    step = get_events_per_slice(config, event_sim_label)
    return range(0, total, step)


def get_event_details(event_label):
    m = re.match(r"1(\w+)-pt(\d+)GeV", event_label)
    if m:
        particle = m.group(1)
        pt = int(m.group(2))
        return "single_particles", {"particle": particle, "pt": pt}
    m = re.match(r"1(\w+)-pt1-100GeV", event_label)
    if m:
        particle = m.group(1)
        return "single_particles", {"particle": particle, "pt_range": (1, 100)}
    m = re.match(r"ttbar-pu(\d+)", event_label)
    if m:
        pu = int(m.group(1))
        return "ttbar", {"pu": pu}
    if event_label == "geantinos":
        return "geantinos", {}
    raise ValueError(f"unknown event: {event_label}")
