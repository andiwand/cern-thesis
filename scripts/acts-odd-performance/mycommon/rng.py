import acts


def get_rng(
    static: bool,
    event_label: str,
) -> acts.examples.RandomNumbers:
    if static:
        return acts.examples.RandomNumbers(seed=42)
    magic = abs(hash(event_label) % 1000)
    return acts.examples.RandomNumbers(seed=magic)
