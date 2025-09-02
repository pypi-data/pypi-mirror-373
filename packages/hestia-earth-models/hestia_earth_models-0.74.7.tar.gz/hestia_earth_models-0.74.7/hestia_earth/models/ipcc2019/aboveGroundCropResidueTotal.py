from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.cropResidue import sum_above_ground_crop_residue
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
    "crop": "IPCC_2019_Ratio_AGRes_YieldDM",
    "forage": "IPCC_2019_Ratio_AGRes_YieldDM"
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


def _product_value(product: dict):
    term = product.get('term', {})
    term_id = product.get('term', {}).get('@id')
    value = list_sum(product.get('value'), default=None)
    dm = get_node_property(product, PROPERTY_KEY).get('value')
    yield_dm = get_yield_dm(TERM_ID, term)
    total = value * dm / 100 * yield_dm if all([
        value is not None,
        dm is not None,
        yield_dm is not None,
    ]) else None
    return {
        'id': term_id,
        'value': value,
        'dryMatter': dm,
        'RatioYieldDM': yield_dm,
        'total': total
    }


def _should_run_product(value: dict): return value.get('total') is not None


def _should_run(cycle: dict):
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    # filter crop products with matching data in the lookup
    products = filter_list_term_type(cycle.get('products', []), [TermTermType.CROP, TermTermType.FORAGE])
    values = list(map(_product_value, products))
    valid_values = list(filter(_should_run_product, values))

    has_crop_forage_products = len(valid_values) > 0

    value = list_sum([(value.get('total') or 0) for value in valid_values], default=None)

    above_ground_crop_residue = sum_above_ground_crop_residue(cycle)
    is_value_below_sum_above_ground_crop_residue = not not value and value >= above_ground_crop_residue

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_crop_forage_products_with_dryMatter=has_crop_forage_products,
                    term_type_cropResidue_incomplete=term_type_incomplete,
                    sum_above_ground_crop_residue=above_ground_crop_residue,
                    value=value,
                    is_value_below_sum_above_ground_crop_residue=is_value_below_sum_above_ground_crop_residue,
                    details=log_as_table(values))

    should_run = all([
        term_type_incomplete,
        has_crop_forage_products,
        value is not None,
        is_value_below_sum_above_ground_crop_residue
    ])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, value


def run(cycle: dict):
    should_run, value = _should_run(cycle)
    return [_product(value)] if should_run else []
