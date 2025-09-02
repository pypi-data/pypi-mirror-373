from hestia_earth.utils.model import linked_node

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "@id": ""
        }
    }
}
RETURNS = {
    "ImpactAssessment": {
        "cycle": {"@type": "Cycle"}
    }
}
MODEL_KEY = 'cycle'


def _run(impact: dict): return linked_node(impact.get(MODEL_KEY))


def _should_run(impact: dict):
    cycle_id = impact.get(MODEL_KEY, {}).get('@id')
    run = cycle_id is not None
    return run


def run(impact: dict): return {**impact, **({MODEL_KEY: _run(impact)} if _should_run(impact) else {})}
