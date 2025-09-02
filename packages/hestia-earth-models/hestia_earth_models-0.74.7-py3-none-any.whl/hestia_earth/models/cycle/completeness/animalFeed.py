from hestia_earth.schema import SiteSiteType

from hestia_earth.models.log import logRequirements
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.animalFeed": "False",
        "site": {
            "@type": "Site",
            "siteType": ["cropland", "glass or high accessible cover"]
        }
    }
}
RETURNS = {
    "Completeness": {
        "animalFeed": ""
    }
}
MODEL_KEY = 'animalFeed'
ALLOWED_SITE_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
]


def run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    site_type_allowed = site_type in ALLOWED_SITE_TYPES

    logRequirements(cycle, model=MODEL, term=None, key=MODEL_KEY,
                    site_type_allowed=site_type_allowed)

    return all([site_type_allowed])
