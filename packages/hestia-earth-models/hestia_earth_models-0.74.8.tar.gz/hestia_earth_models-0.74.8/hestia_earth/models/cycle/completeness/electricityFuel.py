from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logRequirements, log_as_table
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.completeness import _is_term_type_complete
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.operation": "True",
        "completeness.electricityFuel": "False",
        "practices": [
            {"@type": "Practice", "value": "", "term.termType": "operation"}
        ]
    }
}
RETURNS = {
    "Completeness": {
        "electricityFuel": ""
    }
}
LOOKUPS = {
    "operation": ["fuelUse", "combustionType"]
}
MODEL_KEY = 'electricityFuel'
_VALID_COMBUSTION_TYPES = ['mobile', 'stationary']


def _lookup_value(practice: dict, lookup_name: str):
    return get_lookup_value(practice.get('term', {}), lookup_name, model=MODEL, model_key=MODEL_KEY)


def _practice_value(practice: dict):
    term = practice.get('term', {})
    fuel_use = _lookup_value(practice, LOOKUPS['operation'][0])
    return {'id': term.get('@id'), 'value': practice.get('value'), 'fuel_use': fuel_use}


def run(cycle: dict):
    operation_complete = _is_term_type_complete(cycle, TermTermType.OPERATION)
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.OPERATION)
    combustion_practices = [
        p for p in practices if _lookup_value(p, LOOKUPS['operation'][1]) in _VALID_COMBUSTION_TYPES
    ]
    practices_values = list(map(_practice_value, combustion_practices))

    logRequirements(cycle, model=MODEL, term=None, key=MODEL_KEY,
                    term_type_operation_complete=operation_complete,
                    values=log_as_table(practices_values))

    is_complete = all([operation_complete] + [
        all([p.get('fuel_use'), p.get('value') is not None]) for p in practices_values
    ])

    return is_complete
