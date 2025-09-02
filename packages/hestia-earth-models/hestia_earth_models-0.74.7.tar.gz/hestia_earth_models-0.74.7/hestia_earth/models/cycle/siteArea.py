from hestia_earth.schema import TermTermType, SiteSiteType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils import square_meter_to_hectare
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "siteType": "animal housing"
        },
        "none": {
            "otherSites": [{
                "@type": "Site",
                "siteType": "animal housing"
            }]
        },
        "animals": [{
            "@type": "Animal",
            "term.termType": "liveAnimal",
            "value": "> 0"
        }],
        "practices": [{
            "@type": "Practice",
            "term.@id": "stockingDensityAnimalHousingAverage",
            "value": "> 0"
        }]
    }
}
RETURNS = {
    "The siteArea as a number": ""
}
MODEL_KEY = 'siteArea'


def _is_site_valid(site: dict): return site.get('siteType') == SiteSiteType.ANIMAL_HOUSING.value


def _run(cycle: dict):
    animals = filter_list_term_type(cycle.get('animals', []), TermTermType.LIVEANIMAL)
    stocking_density = find_term_match(
        cycle.get('practices', []), 'stockingDensityAnimalHousingAverage', {}).get('value', [])
    return square_meter_to_hectare(round(list_sum([a.get('value') for a in animals]) / list_sum(stocking_density), 7))


def _should_run(cycle: dict, site: dict, key=MODEL_KEY):
    site_type_valid = _is_site_valid(site)
    animals = filter_list_term_type(cycle.get('animals', []), TermTermType.LIVEANIMAL)
    values = [{
        'id': p.get('term', {}).get('@id'),
        'value': p.get('value')
    } for p in animals]
    has_animals = bool(animals)
    stocking_density = list_sum(
        find_term_match(cycle.get('practices', []), 'stockingDensityAnimalHousingAverage', {}).get('value', [-1])
    )

    logRequirements(cycle, model=MODEL, key=key,
                    site_type_valid=site_type_valid,
                    values=log_as_table(values),
                    stocking_density=stocking_density)

    should_run = all([
        site_type_valid,
        has_animals,
        (stocking_density or 0) > 0
    ])
    logShouldRun(cycle, MODEL, None, should_run, key=key)
    return should_run


def run(cycle: dict):
    site = cycle.get('site')
    has_other_sites_valid = any(map(_is_site_valid, cycle.get('otherSites', [])))
    return _run(cycle) if _should_run(cycle, site, key=MODEL_KEY) and not has_other_sites_valid else None
