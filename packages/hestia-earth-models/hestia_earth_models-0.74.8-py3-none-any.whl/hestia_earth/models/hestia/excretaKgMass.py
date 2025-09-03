from hestia_earth.schema import NodeType, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import non_empty_list, list_sum

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import get_kg_term_id, get_kg_N_term_id, get_kg_VS_term_id, _filter_list_term_unit
from hestia_earth.models.utils.term import download_term
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.product import _new_product, convert_product_to_unit
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [
            {
                "@type": "Product",
                "value": "",
                "term.termType": "excreta",
                "term.units": ["kg N", "kg VS"]
            }
        ]
    }
}
RETURNS = {
    "Product": [{
        "term.termType": "excreta",
        "term.units": "kg",
        "value": ""
    }]
}
MODEL_KEY = 'excretaKgMass'

UNITS = [
    Units.KG_N,
    Units.KG_VS
]


def _product(term_id: str, value: float = None):
    product = _new_product(term_id, value, MODEL)
    return product


def _convert_by_product(cycle: dict, product: dict, term_id: str):
    existing_product = find_term_match(cycle.get('products', []), term_id)
    existing_product_value = list_sum(existing_product.get('value', []), default=None)

    conversion_to_kg_ratio = convert_product_to_unit(product, existing_product.get('term', {}).get('units')) \
        if existing_product else None
    value = existing_product_value / conversion_to_kg_ratio if all([
        existing_product_value is not None,
        conversion_to_kg_ratio
    ]) else None

    debugValues(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                using_excreta_product=existing_product.get('term', {}).get('@id'),
                conversion_to_kg_ratio=conversion_to_kg_ratio,
                value=value)

    return value


def _run_product(cycle: dict, product_term_id: str):
    # try to convert from `kg N` first, then `kg VS`
    term_ids = [
        get_kg_N_term_id(product_term_id),
        get_kg_VS_term_id(product_term_id)
    ]

    # convert to 1kg first, then apply ratio to current value
    term = download_term(product_term_id, TermTermType.EXCRETA)
    product = {
        'term': term or {},
        'value': [1]
    }

    values = non_empty_list([_convert_by_product(cycle, product, term_id) for term_id in term_ids])
    value = values[0] if values else None

    # use existing product if exist, else create new one
    existing_product = find_term_match(cycle.get('products', []), product_term_id)

    return (existing_product | _product(product_term_id, value)) if value else _product(product_term_id)


def _should_run(cycle: dict):
    node_type = cycle.get('type', cycle.get('@type'))
    excreta_products = filter_list_term_type(cycle.get('products', []), TermTermType.EXCRETA)
    kg_term_ids = list(set([
        get_kg_term_id(p.get('term', {}).get('@id'))
        for p in _filter_list_term_unit(excreta_products, UNITS)
    ]))
    gap_fill_term_ids = [
        term_id for term_id in kg_term_ids if not find_term_match(excreta_products, term_id).get('value', [])
    ]
    has_gap_fill_term_ids = len(gap_fill_term_ids) > 0

    logRequirements(cycle, model=MODEL, model_key=MODEL_KEY,
                    node_type=node_type,
                    has_gap_fill_term_ids=has_gap_fill_term_ids,
                    gap_fill_term_ids=';'.join(gap_fill_term_ids))

    should_run = all([node_type == NodeType.CYCLE.value, has_gap_fill_term_ids])

    for term_id in gap_fill_term_ids:
        logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)

    logShouldRun(cycle, MODEL, None, should_run)
    return should_run, gap_fill_term_ids


def run(cycle: dict):
    should_run, term_ids = _should_run(cycle)
    return non_empty_list([_run_product(cycle, term_id) for term_id in term_ids]) if should_run else []
