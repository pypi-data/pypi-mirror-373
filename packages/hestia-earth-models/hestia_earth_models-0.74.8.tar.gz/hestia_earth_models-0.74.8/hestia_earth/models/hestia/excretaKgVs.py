from hestia_earth.schema import NodeType, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import _filter_list_term_unit, get_kg_term_id, get_kg_VS_term_id
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.product import _new_product, convert_product_to_unit
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [
            {
                "@type": "Product",
                "term.termType": "excreta",
                "term.units": ["kg"]
            }
        ]
    }
}
RETURNS = {
    "Product": [{
        "term.termType": "excreta",
        "term.units": "kg VS",
        "value": ""
    }]
}
MODEL_KEY = 'excretaKgVs'


def _product(value: float, term_id: str):
    product = _new_product(term_id, value, MODEL)
    return product


def _run_product(cycle: dict, term_id: str):
    existing_kg_product = find_term_match(cycle.get('products', []), get_kg_term_id(term_id))
    value = convert_product_to_unit(existing_kg_product, Units.KG_VS)

    debugValues(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                using_excreta_product=existing_kg_product.get('term', {}).get('@id'),
                value=value)

    # use existing product if exist, else create new one
    existing_product = find_term_match(cycle.get('products', []), term_id)

    return (existing_product | _product(value, term_id)) if value else None


def _should_run(cycle: dict):
    node_type = cycle.get('type', cycle.get('@type'))
    excreta_products = filter_list_term_type(cycle.get('products', []), TermTermType.EXCRETA)
    excreta_products_kg = _filter_list_term_unit(excreta_products, Units.KG)
    kg_N_term_ids = list(set([
        get_kg_VS_term_id(p.get('term', {}).get('@id')) for p in excreta_products_kg
    ]))
    gap_fill_term_ids = [
        term_id for term_id in kg_N_term_ids if not find_term_match(excreta_products, term_id).get('value', [])
    ]
    has_gap_fill_term_ids = len(gap_fill_term_ids) > 0

    logRequirements(cycle, model=MODEL, model_key=MODEL_KEY,
                    node_type=node_type,
                    has_gap_fill_term_ids=has_gap_fill_term_ids,
                    gap_fill_term_ids=';'.join(gap_fill_term_ids))

    should_run = all([node_type == NodeType.CYCLE.value, gap_fill_term_ids])

    for term_id in gap_fill_term_ids:
        logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)

    logShouldRun(cycle, MODEL, None, should_run)
    return should_run, gap_fill_term_ids


def run(cycle: dict):
    should_run, term_ids = _should_run(cycle)
    return non_empty_list([_run_product(cycle, term_id) for term_id in term_ids]) if should_run else []
