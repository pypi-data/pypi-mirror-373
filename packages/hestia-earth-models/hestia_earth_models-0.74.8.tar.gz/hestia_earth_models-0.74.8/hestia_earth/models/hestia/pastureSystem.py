from hestia_earth.schema import TermTermType, SiteSiteType
from hestia_earth.utils.model import find_primary_product, find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.site import valid_site_type
from hestia_earth.models.utils.measurement import measurement_value
from hestia_earth.models.utils.blank_node import most_relevant_blank_node_by_id
from hestia_earth.models.utils.term import get_pasture_system_terms
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "primary": "True",
            "term.termType": "liveAnimal"
        }],
        "site": {
            "@type": "Site",
            "siteType": ["permanent pasture"]
        }
    }
}
RETURNS = {
    "Practice": [{
        "term.termType": "system",
        "value": "100"
    }]
}
MODEL_KEY = 'pastureSystem'
VALID_SITE_TYPES = [SiteSiteType.PERMANENT_PASTURE.value]


def _practice(term_id: str):
    practice = _new_practice(term_id, MODEL)
    practice['value'] = [100]
    return practice


def _run(cycle: dict):
    end_date = cycle.get('endDate')
    measurements = cycle.get('site', {}).get('measurements', [])
    slope = measurement_value(most_relevant_blank_node_by_id(measurements, 'slope', end_date), default=0)
    term_id = 'confinedPastureSystem' if slope <= 2.5 else 'hillyPastureSystem'

    debugValues(cycle, model=MODEL, term=term_id,
                slope=slope)
    logShouldRun(cycle, MODEL, term_id, True)

    return [_practice(term_id)]


def _should_run(cycle: dict):
    product = find_primary_product(cycle)
    product_is_liveAnimal = (product or {}).get('term', {}).get('termType') == TermTermType.LIVEANIMAL.value

    site_type_valid = valid_site_type(cycle.get('site'), site_types=VALID_SITE_TYPES)

    pasture_system_terms = get_pasture_system_terms()
    has_pasture_system = any([find_term_match(cycle.get('practices', []), term_id) for term_id in pasture_system_terms])

    logRequirements(cycle, model=MODEL, term=None, model_key=MODEL_KEY,
                    product_is_liveAnimal=product_is_liveAnimal,
                    site_type_valid=site_type_valid,
                    has_pasture_system=has_pasture_system)

    should_run = all([product_is_liveAnimal, site_type_valid, not has_pasture_system])
    logShouldRun(cycle, MODEL, None, should_run, model_key=MODEL_KEY)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
