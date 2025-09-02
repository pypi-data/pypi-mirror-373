from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import merge_blank_nodes, get_lookup_value
from hestia_earth.models.utils.practice import _new_practice
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
            "practices": [{
                "@type": "Practice",
                "term.termType": "animalManagement"
            }]
        }]
    }
}
LOOKUPS = {
    "region-liveAnimal-milkYieldPerAnimal": "",
    "liveAnimal": ["milkYieldPracticeTermIds", "ipcc2019MilkYieldPerAnimalTermId"]
}
RETURNS = {
    "Animal": [{
        "practices": [{
            "@type": "Practice",
            "value": ""
        }]
    }]
}
MODEL_KEY = 'milkYieldPerAnimal'


def _practice(term_id: str, value: float):
    node = _new_practice(term_id, MODEL)
    node['value'] = [value]
    return node


def _run_animal(data: dict):
    animal = data.get('animal')
    value = data.get('value')
    practice_id = get_lookup_value(animal.get('term'), LOOKUPS['liveAnimal'][1])
    return animal | ({
        'practices': merge_blank_nodes(animal.get('practices', []), [_practice(practice_id, value)])
    } if practice_id else {})


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {})
    country_id = country.get('@id')
    live_animals_with_value = map_live_animals_by_productivity_lookup(
        None, cycle, list(LOOKUPS.keys())[0], practice_column=LOOKUPS['liveAnimal'][0]
    )

    def _should_run_animal(value: dict):
        animal = value.get('animal')
        lookup_value = value.get('value')
        term_id = animal.get('term').get('@id')
        practice = value.get('practice')

        logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                        country_id=country_id,
                        practice=practice.get('term', {}).get('@id'))

        should_run = all([
            country_id,
            lookup_value is not None,
            # must not have the practice already
            not practice
        ])
        logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)

        return should_run

    return list(filter(_should_run_animal, live_animals_with_value))


def run(cycle: dict):
    animals = _should_run(cycle)
    return list(map(_run_animal, animals))
