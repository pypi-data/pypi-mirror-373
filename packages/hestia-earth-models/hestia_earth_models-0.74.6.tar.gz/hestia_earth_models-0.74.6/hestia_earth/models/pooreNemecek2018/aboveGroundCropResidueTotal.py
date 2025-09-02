from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False"
    }
}
LOOKUPS = {
    "crop": "Default_ag_dm_crop_residue"
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
TERM_ID = 'aboveGroundCropResidueTotal'


def _product(value: float):
    product = _new_product(TERM_ID, value, MODEL)
    return product


def _get_lookup_value(product: dict):
    term_id = product.get('term', {}).get('@id', '')
    return safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop']), default=None)


def _run(product: dict):
    value = _get_lookup_value(product)
    return [_product(value)]


def _should_run(cycle: dict):
    # filter crop products with matching data in the lookup
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    product_values = [
        (product, list_sum(product.get('value', [0])), _get_lookup_value(product)) for product in products
    ]
    product_logs = log_as_table([
        {
            'id': product.get('term', {}).get('@id'),
            'value': value,
            'lookup': lookup_value
        } for product, value, lookup_value in product_values
    ])
    products = [
        product for product, value, lookup_value in product_values if all([value > 0, lookup_value is not None])
    ]
    single_crop_product = len(products) == 1
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    product_details=product_logs,
                    single_crop_product=single_crop_product,
                    term_type_cropResidue_incomplete=term_type_incomplete)

    should_run = all([term_type_incomplete, single_crop_product])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products[0]) if should_run else []
