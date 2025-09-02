from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import merge_blank_nodes
from hestia_earth.models.utils.property import _new_property
from .utils import map_live_animals_by_productivity_lookup
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        },
        "animals": [{
            "@type": "Animal",
            "term.termType": "liveAnimal",
            "none": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": "weightAtMaturity"
                }]
            },
            "optional": {
                "properties": [{
                    "@type": "Property",
                    "value": "",
                    "term.@id": "liveweightPerHead"
                }]
            }
        }]
    }
}
LOOKUPS = {
    "region-liveAnimal-weightAtMaturity": ""
}
RETURNS = {
    "Animal": [{
        "properties": [{
            "@type": "Property",
            "value": ""
        }]
    }]
}
TERM_ID = 'weightAtMaturity'


def _property(value: float):
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    return prop


def _run_animal(data: dict):
    animal = data.get('animal')
    value = data.get('value')
    return animal | {
        'properties': merge_blank_nodes(animal.get('properties', []), [_property(value)])
    }


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {})
    country_id = country.get('@id')
    live_animals_with_value = map_live_animals_by_productivity_lookup(TERM_ID, cycle, list(LOOKUPS.keys())[0])

    def _should_run_animal(value: dict):
        animal = value.get('animal')
        lookup_value = value.get('value')
        term_id = animal.get('term').get('@id')
        liveweightPerHead = find_term_match(animal.get('properties', []), 'liveweightPerHead', {})
        liveweightPerHead_value = liveweightPerHead.get('value')

        logRequirements(cycle, model=MODEL, term=term_id, property=TERM_ID,
                        country_id=country_id,
                        weightAtMaturity=lookup_value,
                        liveweightPerHead=liveweightPerHead_value)

        should_run = all([
            country_id,
            lookup_value is not None,
            lookup_value is None or liveweightPerHead_value is None or lookup_value >= liveweightPerHead_value
        ])
        logShouldRun(cycle, MODEL, term_id, should_run, property=TERM_ID)

        return should_run

    return list(filter(_should_run_animal, live_animals_with_value))


def run(cycle: dict):
    animals = _should_run(cycle)
    return list(map(_run_animal, animals))
