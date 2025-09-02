from hestia_earth.utils.model import linked_node

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "@id": ""
        }
    }
}
RETURNS = {
    "ImpactAssessment": {
        "site": {"@type": "Site"}
    }
}
MODEL_KEY = 'site'


def _run(impact: dict): return linked_node(impact.get(MODEL_KEY))


def _should_run(impact: dict):
    site_id = impact.get(MODEL_KEY, {}).get('@id')
    run = site_id is not None
    return run


def run(impact: dict): return {**impact, **({MODEL_KEY: _run(impact)} if _should_run(impact) else {})}
