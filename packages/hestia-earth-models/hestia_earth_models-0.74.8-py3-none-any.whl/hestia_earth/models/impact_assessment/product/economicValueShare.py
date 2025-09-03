from hestia_earth.models.log import logShouldRun
from hestia_earth.models.utils.product import find_by_product
from .. import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "product": {"@type": "Product", "none": {"economicValueShare": ""}},
        "cycle": {
            "@type": "Cycle",
            "products": [{"@type": "Product", "economicValueShare": ""}]
        }
    }
}
RETURNS = {
    "Product": {
        "economicValueShare": ""
    }
}
MODEL_KEY = 'economicValueShare'


def _run(impact: dict, product: dict):
    value = product.get(MODEL_KEY)
    return {**impact.get('product'), MODEL_KEY: value} if value is not None else None


def _should_run(impact: dict):
    product = impact.get('product', {})
    term_id = product.get('term', {}).get('@id')
    value_missing = not product.get(MODEL_KEY)
    cycle = impact.get('cycle', {})
    cycle_product = find_by_product(cycle, product)
    has_cycle_product = cycle_product is not None

    should_run = all([value_missing, has_cycle_product])
    if should_run:
        logShouldRun(impact, MODEL, term_id, should_run, key=MODEL_KEY)

    return should_run, cycle_product


def run(impact: dict):
    should_run, product = _should_run(impact)
    return _run(impact, product) if should_run else None
