from hestia_earth.schema import InputStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun, log_blank_nodes_id
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "term.termType": "crop",
            "value": "> 0"
        }],
        "completeness.other": "False"
    }
}
LOOKUPS = {
    "crop": ["seedPerKgYield", "seedPerKgYield-sd"]
}
RETURNS = {
    "Input": [{
        "value": "",
        "sd": "",
        "statsDefinition": "regions"
    }]
}
TERM_ID = 'seed'


def _input(value: float, sd: float):
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    if sd > 0:
        input['sd'] = [sd]
        input['statsDefinition'] = InputStatsDefinition.REGIONS.value
    return input


def _run_product(product: dict):
    term = product.get('term', {})
    product_value = list_sum(product.get('value', []))
    value = safe_parse_float(
        get_lookup_value(term, LOOKUPS['crop'][0], model=MODEL, term=TERM_ID), default=0) * product_value
    sd = safe_parse_float(get_lookup_value(term, LOOKUPS['crop'][1], model=MODEL, term=TERM_ID), default=0)
    return value, sd


def _run(products: list):
    values = list(map(_run_product, products))
    total_value = list_sum([value for value, _ in values])
    # TODO: we only fill-in sd for single values as the total value is complicated to calculate
    total_sd = values[0][1] if len(values) == 1 else 0
    return [_input(total_value, total_sd)] if total_value > 0 else []


def _should_run_product(product: dict):
    term = product.get('term', {})
    product_value = list_sum(product.get('value', []))
    has_all_lookups = all([get_lookup_value(term, col, model=MODEL, term=TERM_ID) for col in LOOKUPS['crop']])
    return all([has_all_lookups, product_value > 0])


def _should_run(cycle: dict):
    products = cycle.get('products', [])
    crop_products = list(filter(_should_run_product, filter_list_term_type(products, TermTermType.CROP)))
    has_crop_products = len(crop_products) > 0
    term_type_incomplete = _is_term_type_incomplete(cycle, TermTermType.SEED.value)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_seed_incomplete=term_type_incomplete,
                    crop_product_ids=log_blank_nodes_id(crop_products))

    should_run = all([term_type_incomplete, has_crop_products])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, crop_products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products) if should_run else []
