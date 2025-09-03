from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.model import find_term_match, find_primary_product

from hestia_earth.models.log import logRequirements
from hestia_earth.models.utils.crop import is_plantation
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.seed": "False",
        "inputs": [
            {"@type": "Input", "value": "", "term.@id": ["seed", "saplingsDepreciatedAmountPerCycle"]}
        ],
        "site": {
            "@type": "Site",
            "siteType": ["cropland", "glass or high accessible cover"]
        }
    }
}
RETURNS = {
    "Completeness": {
        "seed": ""
    }
}
LOOKUPS = {
    "crop": "isPlantation"
}
MODEL_KEY = 'seed'
ALLOWED_SITE_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
]


def run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    site_type_allowed = site_type in ALLOWED_SITE_TYPES

    has_seed = find_term_match(cycle.get('inputs', []), 'seed', None) is not None

    product = find_primary_product(cycle) or {}
    term_id = product.get('term', {}).get('@id')
    has_saplingsDepreciatedAmountPerCycle = find_term_match(cycle.get('inputs', []),
                                                            'saplingsDepreciatedAmountPerCycle',
                                                            None) and is_plantation(MODEL, None, term_id)

    logRequirements(cycle, model=MODEL, term=None, key=MODEL_KEY,
                    site_type_allowed=site_type_allowed,
                    has_seed=has_seed,
                    has_saplingsDepreciatedAmountPerCycle=has_saplingsDepreciatedAmountPerCycle)

    return all([site_type_allowed, has_seed or has_saplingsDepreciatedAmountPerCycle])
