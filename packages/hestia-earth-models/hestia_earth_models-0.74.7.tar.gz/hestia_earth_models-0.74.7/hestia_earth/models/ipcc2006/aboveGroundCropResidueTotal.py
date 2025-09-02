from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.crop import get_crop_lookup_value
from hestia_earth.models.utils.cropResidue import sum_above_ground_crop_residue
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
    "crop": ["Crop_residue_intercept", "Crop_residue_slope"]
}
RETURNS = {
    "Product": [{
        "value": ""
    }]
}
TERM_ID = 'aboveGroundCropResidueTotal'
PROPERTY_KEY = 'dryMatter'


def _product(value: float):
    product = _new_product(TERM_ID, value, MODEL)
    return product


def _get_value_dm(product: dict, dm_percent: float):
    term_id = product.get('term', {}).get('@id', '')
    product_yield = list_sum(product.get('value', [0]))
    yield_dm = product_yield * (dm_percent / 100) if dm_percent is not None else None

    # estimate the AG DM calculation
    slope = safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop'][1]), default=None)
    intercept = safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop'][0]), default=None)
    debugValues(product, model=MODEL, term=TERM_ID,
                yield_dm=yield_dm,
                dryMatter_percent=dm_percent,
                slope=slope,
                intercept=intercept)
    return None if any([
        slope is None,
        intercept is None,
        yield_dm is None
    ]) else (yield_dm * slope + intercept * 1000)


def _should_run_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    value = list_sum(product.get('value', [0]))
    return value > 0 and (
        safe_parse_float(get_crop_lookup_value(MODEL, TERM_ID, term_id, LOOKUPS['crop'][0]), default=None) is not None
    )


def _should_run(cycle: dict):
    # filter crop products with matching data in the lookup
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROP)
    products = list(filter(_should_run_product, products))
    single_crop_product = len(products) == 1
    dm_property = get_node_property(products[0], PROPERTY_KEY) if single_crop_product else {}
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    dm_value = safe_parse_float(dm_property.get('value'), default=None)
    value = _get_value_dm(products[0], dm_value) if single_crop_product else None

    above_ground_crop_residue = sum_above_ground_crop_residue(cycle)
    is_value_below_sum_above_ground_crop_residue = not not value and value >= above_ground_crop_residue

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    single_crop_product=single_crop_product,
                    nb_products=len(products),
                    dryMatter=dm_property.get('value'),
                    term_type_cropResidue_incomplete=term_type_incomplete,
                    value=value,
                    is_value_below_sum_above_ground_crop_residue=is_value_below_sum_above_ground_crop_residue)

    should_run = all([
        term_type_incomplete,
        single_crop_product,
        value is not None,
        is_value_below_sum_above_ground_crop_residue
    ])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, value


def run(cycle: dict):
    should_run, value = _should_run(cycle)
    return [_product(value)] if should_run else []
