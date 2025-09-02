from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements
from hestia_earth.models.utils.term import get_crop_residue_terms
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "False",
        "products": [
            {"@type": "Product", "value": ">= 0", "term.@id": "belowGroundCropResidue"},
            {"@type": "Product", "value": "> 0", "term.@id": "aboveGroundCropResidueTotal"}
        ],
        "optional": {
            "products": [
                {"@type": "Product", "value": "> 0", "term.@id": "aboveGroundCropResidueRemoved"},
                {"@type": "Product", "value": "> 0", "term.@id": "aboveGroundCropResidueIncorporated"},
                {"@type": "Product", "value": "> 0", "term.@id": "aboveGroundCropResidueBurnt"},
                {"@type": "Product", "value": "> 0", "term.@id": "aboveGroundCropResidueLeftOnField"}
            ]
        }
    }
}
RETURNS = {
    "Completeness": {
        "cropResidue": ""
    }
}
MODEL_KEY = 'cropResidue'
REQUIRED_TERM_IDS = [
    'belowGroundCropResidue',
    'aboveGroundCropResidueTotal'
]


def _optional_term_ids():
    terms = get_crop_residue_terms()
    return [term for term in terms if term not in REQUIRED_TERM_IDS]


def _has_product(products, zero_allowed=True):
    def has_product(term_id: str):
        value = list_sum(find_term_match(products, term_id).get('value', [-1]))
        return (term_id, value >= 0 if zero_allowed else value > 0)
    return has_product


def run(cycle: dict):
    products = cycle.get('products', [])
    # all required terms + at least one of the optional terms must be present
    required_products_map = [
        _has_product(products, zero_allowed=True)('belowGroundCropResidue'),
        _has_product(products, zero_allowed=False)('aboveGroundCropResidueTotal'),
    ]
    optional_products_map = list(map(_has_product(products, zero_allowed=False), _optional_term_ids()))

    has_required_products = all([has_product for _term_id, has_product in required_products_map])
    has_optional_product = any([has_product for _term_id, has_product in optional_products_map])

    logRequirements(cycle, model=MODEL, term=None, key=MODEL_KEY,
                    **({
                        f'has_required_{term_id}': has_product for term_id, has_product in required_products_map
                    } | {
                        f'has_optional_{term_id}': has_product for term_id, has_product in optional_products_map
                    }))

    return all([has_required_products, has_optional_product])
