from hestia_earth.schema import SchemaType

from hestia_earth.models.utils import _load_calculated_node

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


def _run(impact: dict):
    cycle = _load_calculated_node(impact.get(MODEL_KEY, {}), SchemaType.CYCLE)
    site = _load_calculated_node(cycle.get('site', {}), SchemaType.SITE)
    if site:
        cycle['site'] = site

    # need to download `otherSites` as well
    if 'otherSites' in cycle:
        cycle['otherSites'] = [_load_calculated_node(s, SchemaType.SITE) for s in cycle['otherSites']]

    return cycle


def _should_run(impact: dict):
    cycle_id = impact.get(MODEL_KEY, {}).get('@id')
    run = cycle_id is not None
    return run


def run(impact: dict): return {**impact, **({MODEL_KEY: _run(impact)} if _should_run(impact) else {})}
