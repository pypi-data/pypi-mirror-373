from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_primary_product, linked_node
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues, log_as_table
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.crop import is_plantation
from hestia_earth.models.utils.cycle import get_allowed_sites
from .utils import get_region_factor
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "or": [
                {"region": {"@type": "Term", "termType": "region"}},
                {"country": {"@type": "Term", "termType": "region"}}
            ]
        },
        "optional": {
            "otherSites": [
                {
                    "@type": "Site",
                    "or": [
                        {"region": {"@type": "Term", "termType": "region"}},
                        {"country": {"@type": "Term", "termType": "region"}}
                    ]
                }
            ]
        }
    }
}
RETURNS = {
    "Practice": [{
        "value": "",
        "site": ""
    }]
}
LOOKUPS = {
    "crop": "isPlantation",
    "region-landUseManagement": "croppingIntensity"
}
TERM_ID = 'croppingIntensity'


def _practice(site: dict, value: float):
    practice = _new_practice(TERM_ID)
    practice['site'] = linked_node(site)
    # force conversion to float from numpy, avoiding errors when reading it in other models
    practice['value'] = [float(round(value, 7))]
    return practice


def _should_run(cycle: dict):
    product = find_primary_product(cycle) or {}
    not_plantation = not is_plantation(MODEL, TERM_ID, product.get('term', {}).get('@id'))

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    not_plantation=not_plantation)

    should_run = all([not_plantation])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict):
    sites = get_allowed_sites(MODEL, TERM_ID, cycle) if _should_run(cycle) else []
    sites = [
        (site, get_region_factor(TERM_ID, site, TermTermType.LANDUSEMANAGEMENT)) for site in sites
    ]

    debugValues(cycle, model=MODEL, term=TERM_ID,
                site_factors=log_as_table([{
                    'site-id': site.get('@id', site.get('id')),
                    'factor': factor
                } for site, factor in sites]))

    return non_empty_list([_practice(site, factor) for site, factor in sites if bool(factor)])
