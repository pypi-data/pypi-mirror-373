from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{"@type": "Input", "value": "", "term.@id": "machineryInfrastructureDepreciatedAmountPerCycle"}],
        "site": {
            "@type": "Site",
            "siteType": ["cropland", "glass or high accessible cover"]
        }
    }
}
RETURNS = {
    "Completeness": {
        "material": ""
    }
}
MODEL_KEY = 'material'
ALLOWED_SITE_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
]


def run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    site_type_allowed = site_type in ALLOWED_SITE_TYPES
    has_machinery_input = find_term_match(
        cycle.get('inputs', []), 'machineryInfrastructureDepreciatedAmountPerCycle', None
    ) is not None

    logRequirements(cycle, model=MODEL, term=None, key=MODEL_KEY,
                    site_type_allowed=site_type_allowed,
                    has_machinery_input=has_machinery_input)

    return all([site_type_allowed, has_machinery_input])
