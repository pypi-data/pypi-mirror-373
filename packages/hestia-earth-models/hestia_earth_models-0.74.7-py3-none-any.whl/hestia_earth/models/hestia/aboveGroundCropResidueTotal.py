from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.cropResidue import PRODUCT_ID_TO_PRACTICES_ID
from hestia_earth.models.utils.product import _new_product
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "practices": [{"@type": "Practice", "value": "", "term.termType": "cropResidue"}],
        "products": [{"@type": "Product", "value": "", "term.termType": "cropResidueManagement"}]
    }
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


def _run(practice: dict, product: dict):
    practice_value = list_sum(practice.get('value', []))
    product_value = list_sum(product.get('value', []))
    value = product_value / (practice_value / 100)
    return [_product(round(value, 7))]


def _matching_product_by_practice(term_id: str):
    return next((v.get('product') for v in PRODUCT_ID_TO_PRACTICES_ID if term_id in v.get('practices')), None)


def _should_run(cycle: dict):
    # run if any practice with a value matches a product with a value
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROPRESIDUE)

    def _matching_product(practice: dict):
        practice_term_id = practice.get('term', {}).get('@id')
        product_term_id = _matching_product_by_practice(practice_term_id)
        product = find_term_match(products, product_term_id)

        practice_value = list_sum(practice.get('value', []))
        product_value = list_sum(product.get('value', []))

        return (practice, product) if all([practice_value, product_value]) else None

    matching_practices = non_empty_list(map(_matching_product, practices))
    practice, matching_product = (matching_practices or [(None, None)])[0]

    practice_id = (practice or {}).get('term', {}).get('@id')
    product_id = (matching_product or {}).get('term', {}).get('@id')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    practice_id=practice_id,
                    product_id=product_id)

    should_run = all([practice_id, product_id])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, practice, matching_product


def run(cycle: dict):
    should_run, practice, matching_product = _should_run(cycle)
    return _run(practice, matching_product) if should_run else []
