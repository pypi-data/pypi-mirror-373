from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "products": [{
            "@type": "Product",
            "primary": "True",
            "optional": {
                "properties": [{"@type": "Property", "value": "", "term.@id": "dryMatter"}]
            }
        }]
    }
}
LOOKUPS = {
    "crop": "isAboveGroundCropResidueRemoved"
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
TERM_ID = 'aboveGroundCropResidueRemoved'
PROPERTY_KEY = 'dryMatter'


def _product(value: float):
    product = _new_product(TERM_ID, value, MODEL)
    return product


def _get_value(product: dict, product_dm_property: dict):
    value = product.get('value', [0])[0]
    dm_percent = safe_parse_float(product_dm_property.get('value'), default=None)
    debugValues(product, model=MODEL, term=product.get('term', {}).get('@id'),
                value=value,
                dm_percent=dm_percent)
    return value * dm_percent / 100 if dm_percent is not None else 0


def _run(products: list):
    value = sum([_get_value(product, dm_prop) for product, dm_prop in products])
    return [_product(value)] if value is not None else []


def _should_run_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    product_match = get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop'])
    property = get_node_property(product, PROPERTY_KEY) if product_match else None
    debugValues(product, model=MODEL, term=TERM_ID,
                product=term_id,
                product_match=product_match)
    return [product, property] if property else []


def _should_run(cycle: dict):
    products = non_empty_list(map(_should_run_product, cycle.get('products', [])))
    has_products_with_dryMatter = len(products) > 0
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_products_with_dryMatter=has_products_with_dryMatter,
                    term_type_cropResidue_incomplete=term_type_incomplete)

    should_run = all([has_products_with_dryMatter, term_type_incomplete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, products


def run(cycle: dict):
    should_run, products = _should_run(cycle)
    return _run(products) if should_run else []
