from hestia_earth.schema import SiteSiteType, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements
from hestia_earth.models.utils import is_from_model
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.freshForage": "False",
        "site": {
            "@type": "Site",
            "siteType": "permanent pasture"
        },
        "or": {
            "inputs": [{"@type": "Input", "termType": "forage", "value": ">= 0", "added": ["value"]}],
            "animals": [{
                "@type": "Animal",
                "inputs": [{"@type": "Input", "termType": "forage", "value": ">= 0", "added": ["value"]}]
            }]
        }
    }
}
RETURNS = {
    "Completeness": {
        "freshForage": ""
    }
}
LOOKUPS = {
    "liveAnimal": "isGrazingAnimal",
    "liveAquaticSpecies": "isGrazingAnimal"
}
MODEL_KEY = 'freshForage'
ALLOWED_SITE_TYPES = [
    SiteSiteType.PERMANENT_PASTURE.value
]


def _valid_input(input: dict): return is_from_model(input) and list_sum(input.get('value', [-1])) >= 0


def _inputs(node: dict): return filter_list_term_type(node.get('inputs', []), TermTermType.FORAGE)


def run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    site_type_allowed = site_type in ALLOWED_SITE_TYPES

    cycle_has_added_forage_input = any(map(_valid_input, _inputs(cycle)))

    animals = [
        a for a in cycle.get('animals', [])
        if get_lookup_value(a.get('term', {}), 'isGrazingAnimal', model=MODEL, key=MODEL_KEY)
    ]
    all_animals_have_added_forage_input = bool(animals) and all([
        any(map(_valid_input, _inputs(animal))) for animal in animals
    ])

    logRequirements(cycle, model=MODEL, term=None, key=MODEL_KEY,
                    site_type_allowed=site_type_allowed,
                    cycle_has_added_forage_input=cycle_has_added_forage_input,
                    all_animals_have_added_forage_input=all_animals_have_added_forage_input)

    return all([site_type_allowed, cycle_has_added_forage_input or all_animals_have_added_forage_input])
