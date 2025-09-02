from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logShouldRun, logRequirements, log_blank_nodes_id
from hestia_earth.models.utils.blank_node import merge_blank_nodes
from hestia_earth.models.utils.term import get_lookup_value
from .. import MODEL

REQUIREMENTS = {
    "Cycle": {
        "animals": [{
            "@type": "Animal",
            "term.termType": "liveAnimal"
        }],
        "practices": [{
            "@type": "Practice",
            "term.termType": "animalManagement"
        }]
    }
}
RETURNS = {
    "Animal": [{
        "practices": [{
            "@type": "Practice",
            "term.termType": "animalManagement"
        }]
    }]
}
LOOKUPS = {
    "liveAnimal": "milkYieldPracticeTermIds"
}

MODEL_KEY = 'milkYield'


def _run(cycle: dict, animal: dict):
    term = animal.get('term', {})
    term_id = term.get('@id')
    value = get_lookup_value(term, LOOKUPS['liveAnimal'], model=MODEL, model_key=MODEL_KEY)
    practice_ids = non_empty_list((value or '').split(';'))
    practices = non_empty_list(
        [p for p in cycle.get('practices', []) if p.get('term', {}).get('@id') in practice_ids]
    )
    log_args = {
        'model_key': MODEL_KEY,
        'animalId': animal.get('animalId')
    }

    logRequirements(cycle, model=MODEL, term=term_id,
                    practice_ids=log_blank_nodes_id(practices),
                    **log_args)

    for practice in practices:
        logShouldRun(cycle, MODEL, practice.get('term', {}).get('@id'), True, **log_args)

    return {
        **animal,
        'practices': merge_blank_nodes(animal.get('practices', []), practices)
    } if practices else None


def _should_run(cycle: dict):
    animals = filter_list_term_type(cycle.get('animals', []), TermTermType.LIVEANIMAL)
    has_animals = len(animals) > 0

    should_run = all([has_animals])
    logShouldRun(cycle, MODEL, None, should_run, model_key=MODEL_KEY)
    return should_run, animals


def run(cycle: dict):
    should_run, animals = _should_run(cycle)
    return non_empty_list([_run(cycle, a) for a in animals]) if should_run else []
