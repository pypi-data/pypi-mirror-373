from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "value": "", "term.termType": "crop"}]
    }
}
LOOKUPS = {
    "crop": "Plantation_longFallowDuration"
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
TERM_ID = 'longFallowDuration'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    return practice


def _get_value(product: dict):
    term_id = product.get('term', {}).get('@id', '')
    return safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop']), default=None)


def _run(product: dict):
    value = _get_value(product)
    return [_practice(value)]


def _should_run_product(product: dict): return _get_value(product) is not None


def _should_run(cycle: dict):
    product = next((p for p in cycle.get('products', []) if _should_run_product(p)), None)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    crop_product_id=(product or {}).get('term', {}).get('@id'))

    should_run = all([product])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, product


def run(cycle: dict):
    should_run, product = _should_run(cycle)
    return _run(product) if should_run else []
