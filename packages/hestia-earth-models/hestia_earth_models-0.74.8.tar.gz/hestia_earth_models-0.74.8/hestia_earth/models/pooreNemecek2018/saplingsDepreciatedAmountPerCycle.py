from hestia_earth.utils.tools import safe_parse_float, list_sum
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL
from .plantationLifespan import TERM_ID as PRACTICE_TERM_ID

REQUIREMENTS = {
    "Cycle": {
        "completeness.other": "False",
        "cycleDuration": "> 0",
        "products": [{"@type": "Product", "value": "", "term.termType": "crop"}],
        "practices": [{"@type": "Practice", "value": "", "term.@id": "plantationLifespan"}]
    }
}
LOOKUPS = {
    "crop": "Saplings_required"
}
RETURNS = {
    "Input": [{
        "value": ""
    }]
}
TERM_ID = 'saplingsDepreciatedAmountPerCycle'


def _input(value: float):
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    return input


def _get_value(product: dict):
    term_id = product.get('term', {}).get('@id', '')
    return safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop']), default=None)


def _run(product: dict, plantationLifespan: float, cycleDuration: float):
    value = _get_value(product)
    return [_input(value / plantationLifespan * cycleDuration)]


def _should_run_product(product: dict): return _get_value(product) is not None


def _should_run(cycle: dict):
    cycleDuration = cycle.get('cycleDuration')
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)
    product = next((p for p in cycle.get('products', []) if _should_run_product(p)), None)
    plantationLifespan = list_sum(find_term_match(cycle.get('practices', []), PRACTICE_TERM_ID).get('value'), None)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_seed_incomplete=term_type_incomplete,
                    product_id=(product or {}).get('term', {}).get('@id'),
                    plantationLifespan=plantationLifespan,
                    cycleDuration=cycleDuration)

    should_run = all([term_type_incomplete, product, plantationLifespan, (cycleDuration or 0) > 0])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, product, plantationLifespan, cycleDuration


def run(cycle: dict):
    should_run, product, plantationLifespan, cycleDuration = _should_run(cycle)
    return _run(product, plantationLifespan, cycleDuration) if should_run else []
