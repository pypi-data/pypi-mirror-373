from functools import reduce
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table, log_blank_nodes_id
from hestia_earth.models.utils import is_from_model
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.term import get_crop_residue_management_terms
from hestia_earth.models.utils.cropResidue import crop_residue_product_ids
from . import MODEL


def _practice(term_id: str, value: float):
    practice = _new_practice(term_id, MODEL)
    practice['value'] = [value]
    return practice


def _model_value(term_id: str, practices: list):
    return list_sum(find_term_match(practices, term_id).get('value', [0]))


def _should_run(term_id: str, cycle: dict, require_country: bool = False):
    primary_product = find_primary_product(cycle)
    has_primary_product = primary_product is not None

    crop_residue_incomplete = _is_term_type_incomplete(cycle, TermTermType.CROPRESIDUE)
    practices = cycle.get('practices', [])
    residue_terms = get_crop_residue_management_terms()
    remaining_value = reduce(lambda prev, term: prev - _model_value(term, practices), residue_terms, 100)
    residue_values = log_as_table([
        {'id': term_id, 'value': _model_value(term_id, practices)} for term_id in residue_terms
    ])
    has_remaining_value = remaining_value > 0

    # make sure no above ground residue product has been added by the user, or values will be off
    provided_cropResidue_products = [
        p for p in cycle.get('products', []) if all([
            p.get('term', {}).get('@id') in crop_residue_product_ids(),
            p.get('value', []),
            not is_from_model(p)
        ])
    ]
    no_provided_cropResidue_products = len(provided_cropResidue_products) == 0

    country_id = cycle.get('site', {}).get('country', {}).get('@id')

    logRequirements(cycle, model=MODEL, term=term_id,
                    has_primary_product=has_primary_product,
                    term_type_cropResidue_incomplete=crop_residue_incomplete,
                    has_remaining_value=has_remaining_value,
                    crop_residue_values=residue_values,
                    country_id=country_id,
                    no_provided_cropResidue_products=no_provided_cropResidue_products,
                    provided_cropResidue_product_ids=log_blank_nodes_id(provided_cropResidue_products))

    should_run = all([
        has_primary_product, crop_residue_incomplete, has_remaining_value,
        not require_country or country_id,
        no_provided_cropResidue_products
    ])
    logShouldRun(cycle, MODEL, term_id, should_run)
    return should_run, remaining_value, primary_product, country_id
