from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils import weighted_average
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.practice import _new_practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "animals": [{
            "@type": "Animal",
            "term.termType": "liveAnimal",
            "value": "> 0"
        }]
    }
}
RETURNS = {
    "Practice": [{
        "value": ""
    }]
}
LOOKUPS = {
    "liveAnimal": "stockingDensityAnimalHousing"
}
TERM_ID = 'stockingDensityAnimalHousingAverage'


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [round(value, 7)]
    return practice


def _run(values: list):
    # take a weighted average
    value = weighted_average([
        (p.get('lookup'), p.get('value')) for p in values
    ])
    return [_practice(value)]


def _should_run(cycle: dict):
    animals = filter_list_term_type(cycle.get('animals', []), TermTermType.LIVEANIMAL)
    values = [{
        'id': p.get('term', {}).get('@id'),
        'value': p.get('value'),
        'lookup': get_lookup_value(p.get('term', {}), LOOKUPS['liveAnimal'])
    } for p in animals]
    has_animals = bool(animals)
    has_values = all([all([p.get('value') is not None, p.get('lookup') is not None]) for p in values])

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    values=log_as_table(values))

    should_run = all([has_animals, has_values])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, values


def run(cycle: dict):
    should_run, values = _should_run(cycle)
    return _run(values) if should_run else []
