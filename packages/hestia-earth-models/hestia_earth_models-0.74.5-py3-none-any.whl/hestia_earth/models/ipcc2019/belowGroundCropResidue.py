from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.term import get_lookup_value
from .utils import get_yield_dm
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "products": [{
            "@type": "Product",
            "term.termType": ["crop", "forage"],
            "value": "> 0",
            "optional": {
                "properties": [{"@type": "Property", "value": "", "term.@id": "dryMatter"}]
            }
        }]
    }
}
LOOKUPS = {
    "crop": ["IPCC_2019_Ratio_AGRes_YieldDM", "IPCC_2019_Ratio_BGRes_AGRes"],
    "forage": ["IPCC_2019_Ratio_AGRes_YieldDM", "IPCC_2019_Ratio_BGRes_AGRes"]
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
TERM_ID = 'belowGroundCropResidue'
PROPERTY_KEY = 'dryMatter'


def _product(value: float):
    product = _new_product(TERM_ID, value, MODEL)
    return product


def _get_lookup_value(term: dict, column: str):
    return safe_parse_float(get_lookup_value(term, column, model=MODEL, term=TERM_ID), default=None)


def _product_value(product: dict):
    term = product.get('term', {})
    term_id = product.get('term', {}).get('@id')
    value = list_sum(product.get('value'))
    dm = get_node_property(product, PROPERTY_KEY).get('value', 0)
    yield_dm = get_yield_dm(TERM_ID, term) or 0
    ratio = _get_lookup_value(term, 'IPCC_2019_Ratio_BGRes_AGRes') or 0
    total = value * dm / 100 * yield_dm * ratio
    return {
        'id': term_id,
        'value': value,
        'dryMatter': dm,
        'RatioYieldDM': yield_dm,
        'RatioAboveGroundToBelowGround': ratio,
        'total': total
    }


def _run(cycle: dict, products: list):
    values = list(map(_product_value, products))
    debugValues(cycle, model=MODEL, term=TERM_ID,
                details=log_as_table(values))
    value = sum([value.get('total', 0) for value in values])
    return [_product(value)]


def _should_run_product(product: dict):
    term = product.get('term', {})
    value = list_sum(product.get('value', [0]))
    prop = get_node_property(product, PROPERTY_KEY).get('value')
    yield_dm = get_yield_dm(TERM_ID, term)
    return all([value > 0, prop, yield_dm is not None])


def _should_run(cycle: dict):
    # filter crop products with matching data in the lookup
    products = filter_list_term_type(cycle.get('products', []), [TermTermType.CROP, TermTermType.FORAGE])
    products = list(filter(_should_run_product, products))
    has_crop_forage_products = len(products) > 0
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_crop_forage_products_with_dryMatter=has_crop_forage_products,
                    term_type_cropResidue_incomplete=term_type_incomplete)

    should_run = all([term_type_incomplete, has_crop_forage_products])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(cycle, products) if should_run else []
