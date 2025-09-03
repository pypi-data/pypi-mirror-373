from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import flatten, list_sum

from .completeness import _is_term_type_complete

PRODUCT_ID_TO_PRACTICES_ID = [
    {'product': 'aboveGroundCropResidueRemoved', 'practices': ['residueRemoved']},
    {'product': 'aboveGroundCropResidueIncorporated', 'practices': [
        'residueIncorporated',
        'residueIncorporatedLessThan30DaysBeforeCultivation',
        'residueIncorporatedMoreThan30DaysBeforeCultivation'
    ]},
    {'product': 'aboveGroundCropResidueBurnt', 'practices': ['residueBurnt']},
    {'product': 'aboveGroundCropResidueLeftOnField', 'practices': ['residueLeftOnField']}
]


def crop_residue_product_ids(): return [v.get('product') for v in PRODUCT_ID_TO_PRACTICES_ID]


def get_crop_residue_burnt_value(cycle: dict):
    products = cycle.get('products', [])
    value = flatten([
        find_term_match(products, 'aboveGroundCropResidueBurnt').get('value', []),
        find_term_match(products, 'discardedCropBurnt').get('value', [])
    ])
    data_complete = _is_term_type_complete(cycle, TermTermType.CROPRESIDUE)
    return 0 if len(value) == 0 and data_complete else list_sum(value, default=None)


def sum_above_ground_crop_residue(cycle: dict):
    products = [p for p in cycle.get('products', []) if p.get('term', {}).get('@id') in crop_residue_product_ids()]
    return list_sum(value=flatten([v.get('value') or [] for v in products]), default=0)
