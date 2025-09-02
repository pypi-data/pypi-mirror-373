from hestia_earth.schema import EmissionMethodTier, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.lookup import extract_grouped_data
from hestia_earth.utils.blank_node import group_by_keys
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.term import get_lookup_value
from .utils import _emission
from . import MODEL

_TIER = EmissionMethodTier.TIER_1.value


def _run_inputs(inputs: list, tier: str, term_id: str):
    total_value = list_sum([
        (i.get('input-value') or 0) * (i.get('operation-factor') or i.get('input-default-factor') or 0)
        for i in inputs
    ])
    input_term = {
        '@type': 'Term',
        '@id': inputs[0].get('input-id'),
        'termType': inputs[0].get('input-termType'),
        'units': inputs[0].get('input-units'),
    }
    operation_term = {
        '@type': 'Term',
        '@id': inputs[0].get('operation-id'),
        'termType': inputs[0].get('operation-termType'),
        'units': inputs[0].get('operation-units'),
    } if inputs[0].get('operation-id') else None
    return _emission(
        value=total_value,
        tier=tier,
        term_id=term_id,
        input=input_term,
        operation=operation_term
    )


def _fuel_input_data(term_id: str, lookup_col: str, input: dict):
    input_term = input.get('term', {})
    input_term_id = input_term.get('@id')
    operation_term = input.get('operation', {})
    input_value = list_sum(input.get('value', []), None)

    operation_factor = extract_grouped_data(
        data=get_lookup_value(operation_term, lookup_col, model=MODEL, term=term_id),
        key=input_term_id
    ) if operation_term else None
    input_factor = get_lookup_value(input_term, lookup_col, model=MODEL, term=term_id)

    return {
        'input-id': input_term_id,
        'input-termType': input_term.get('termType'),
        'input-units': input_term.get('units'),
        'input-value': input_value,
        'input-default-factor': safe_parse_float(input_factor, default=None),
        'operation-id': operation_term.get('@id'),
        'operation-termType': operation_term.get('termType'),
        'operation-units': operation_term.get('units'),
        'operation-factor': safe_parse_float(operation_factor, default=None)
    }


def get_fuel_inputs(term_id: str, cycle: dict, lookup_col: str):
    inputs = [
        _fuel_input_data(term_id, lookup_col, i)
        for i in filter_list_term_type(cycle.get('inputs', []), TermTermType.FUEL)
    ]
    valid_inputs = [
        i for i in inputs if all([
            i.get('input-value') is not None,
            (i.get('operation-factor') or i.get('input-default-factor')) is not None
        ])
    ]
    return inputs, valid_inputs


def group_fuel_inputs(inputs: list):
    return group_by_keys(inputs, ['input-id', 'operation-id']) if len(inputs) > 0 else None


def _should_run(cycle: dict, term_id: str, lookup_prefix: str = None):
    electricity_complete = _is_term_type_complete(cycle, 'electricityFuel')
    fuel_inputs, valid_inputs = get_fuel_inputs(term_id, cycle, f"{lookup_prefix or term_id}EmepEea2019")

    logRequirements(cycle, model=MODEL, term=term_id,
                    termType_electricityFuel_complete=electricity_complete,
                    fuel_inputs=log_as_table(fuel_inputs))

    should_run = any([bool(valid_inputs), electricity_complete])
    logShouldRun(cycle, MODEL, term_id, should_run, methodTier=_TIER)
    return should_run, group_fuel_inputs(valid_inputs)


def run(cycle: dict, term_id: str, lookup_prefix: str = None):
    should_run, fuel_inputs = _should_run(cycle, term_id, lookup_prefix)
    return (
        [
            _run_inputs(inputs, tier=_TIER, term_id=term_id)
            for inputs in fuel_inputs.values()
        ] if fuel_inputs else [
            _emission(value=0, tier=_TIER, term_id=term_id)
        ]
    ) if should_run else []
