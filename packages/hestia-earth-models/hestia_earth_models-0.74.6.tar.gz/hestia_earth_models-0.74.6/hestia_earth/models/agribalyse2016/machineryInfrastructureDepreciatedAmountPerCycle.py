from hestia_earth.utils.tools import list_sum, flatten

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues, log_as_table
from hestia_earth.models.utils.productivity import get_productivity, PRODUCTIVITY
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from hestia_earth.models.utils.term import get_liquid_fuel_terms
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "term.termType": "fuel",
            "value": ""
        }],
        "completeness.material": "False",
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        }
    }
}
LOOKUPS = {
    "region": "HDI"
}
RETURNS = {
    "Input": [{
        "value": ""
    }]
}
TERM_ID = 'machineryInfrastructureDepreciatedAmountPerCycle'


def _input(value: float):
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    return input


def _get_input_value_from_term(inputs: list, term_id: str):
    values = flatten([
        input.get('value', []) for input in inputs if input.get('term', {}).get('@id') == term_id
    ])
    return list_sum(values, 0) if len(values) > 0 else None


def get_value(country: dict, cycle: dict):
    liquid_fuels = get_liquid_fuel_terms()
    productivity_key = get_productivity(country)
    machinery_usage = 11.5 if productivity_key == PRODUCTIVITY.HIGH else 23
    values = [(term_id, _get_input_value_from_term(cycle.get('inputs', []), term_id)) for term_id in liquid_fuels]
    value_logs = log_as_table([{'id': term_id, 'value': value} for term_id, value in values])
    values = [value for term_id, value in values if value is not None]
    fuel_use = list_sum(values, 0)
    debugValues(cycle, model=MODEL, term=TERM_ID,
                productivity_key=productivity_key.value,
                fuel_use_details=value_logs,
                fuel_use=fuel_use)
    return fuel_use/machinery_usage if fuel_use > 0 else None


def _run(cycle: dict):
    country = cycle.get('site', {}).get('country', {})
    value = get_value(country, cycle)
    return [_input(value)] if value is not None else []


def _should_run(cycle: dict):
    term_type_incomplete = _is_term_type_incomplete(cycle, TERM_ID)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_material_incomplete=term_type_incomplete)

    should_run = all([term_type_incomplete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
