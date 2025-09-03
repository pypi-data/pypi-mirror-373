from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, flatten

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils.cropResidueManagement import has_residue_incorporated_practice
from . import MODEL, residueBurnt, residueIncorporated, residueLeftOnField, residueRemoved

REQUIREMENTS = {
    "Cycle": {
        "practices": [
            {"@type": "Practice", "term.termType": "cropResidueManagement", "value": "100"}
        ]
    }
}
RETURNS = {
    "Practice": [{
        "value": "",
        "term.termType": "cropResidueManagement"
    }]
}
MODEL_KEY = 'cropResidueManagement'
PRACTICE_IDS = [
    residueBurnt.TERM_ID,
    residueIncorporated.TERM_ID,
    residueLeftOnField.TERM_ID,
    residueRemoved.TERM_ID,
    'residueIncorporatedLessThan30DaysBeforeCultivation',
    'residueIncorporatedMoreThan30DaysBeforeCultivation',
]


def _practice(term_id: str):
    practice = _new_practice(term_id, MODEL)
    practice['value'] = [0]
    return practice


def _should_run(cycle: dict):
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    sum_practices = list_sum(flatten([p.get('value', []) for p in practices]))
    existing_practices = [p.get('term', {}).get('@id') for p in practices]
    # remove incorporated if any of the similar ones are present
    practice_ids = [term_id for term_id in PRACTICE_IDS if any([
        term_id != residueIncorporated.TERM_ID,
        not has_residue_incorporated_practice(cycle)
    ])]
    missing_practices = [term_id for term_id in practice_ids if term_id not in existing_practices]

    should_run = all([99.5 <= sum_practices <= 100.5])

    for term_id in missing_practices:
        logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                        sum_crop_residue_management=sum_practices)

        logShouldRun(cycle, MODEL, term_id, should_run, model_key=MODEL_KEY)

    return should_run, missing_practices


def run(cycle: dict):
    should_run, missing_practices = _should_run(cycle)
    return list(map(_practice, missing_practices)) if should_run else []
