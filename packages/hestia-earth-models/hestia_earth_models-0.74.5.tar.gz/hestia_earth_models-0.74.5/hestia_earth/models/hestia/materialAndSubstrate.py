from typing import Union
from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import download_lookup, lookup_term_ids
from hestia_earth.utils.tools import to_precision, flatten, list_sum
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logShouldRun, logRequirements
from hestia_earth.models.utils.constant import DAYS_IN_YEAR
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.completeness import _is_term_type_incomplete
from .import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.material": "False",
        "cycleDuration": "",
        "site": {
            "@type": "Site",
            "infrastructure": [
                {
                    "@type": "Infrastructure",
                    "defaultLifespan": "",
                    "inputs": [
                        {
                            "@type": "Input",
                            "term.termType": ["material", "substrate"],
                            "value": "",
                            "lifespan": ""
                        }
                    ]
                }
            ]
        }
    }
}
RETURNS = {
    "Input": [{
        "value": "",
        "min": "",
        "max": "",
        "sd": "",
        "statsDefinition": ""
    }]
}
LOOKUPS = {
    "material": ""
}
MODEL_KEY = 'materialAndSubstrate'

_ID_SUFFIX = "DepreciatedAmountPerCycle"
_OPTIONAL_VALUES = ["min", "max", "sd"]
_SIGNIFICANT_DIGITS = 5


def _input(term_id: str, value: float, stats: dict) -> dict:
    node = _new_input(term_id + _ID_SUFFIX, MODEL)
    node['value'] = [value]
    return node | stats


def _get_value(node: dict, field_name: str) -> float:
    value = node.get(field_name)
    return list_sum(value) if isinstance(value, list) else value


def calculate_value(input_node: dict, field_name: str, cycle_duration: float) -> Union[float, None]:
    lifespan = input_node.get("lifespan")
    value = _get_value(node=input_node, field_name=field_name)
    return (
        to_precision(number=(value / (lifespan * DAYS_IN_YEAR)) * cycle_duration, digits=_SIGNIFICANT_DIGITS)
        if value else None
    )


def _run_input(cycle: dict, input_node: dict) -> dict:
    cycle_duration = cycle.get("cycleDuration")

    value = calculate_value(
        input_node=input_node,
        field_name="value",
        cycle_duration=cycle_duration
    )

    optional_gap_filled_values = {
        field_name: [
            calculate_value(input_node=input_node, field_name=field_name, cycle_duration=cycle_duration)
        ]
        for field_name in _OPTIONAL_VALUES if field_name in input_node
    }
    if "statsDefinition" in input_node:
        optional_gap_filled_values["statsDefinition"] = input_node["statsDefinition"]

    return _input(input_node.get('term', {}).get('@id'), value, optional_gap_filled_values)


def _has_depreciated_term(term: dict):
    lookup = download_lookup(f"{term.get('termType')}.csv")
    term_ids = lookup_term_ids(lookup)
    return term.get('@id') + _ID_SUFFIX in term_ids


def _should_run_input(cycle: dict, input_node: dict) -> bool:
    term = input_node.get('term', {})
    term_id = term.get('@id')
    has_lifespan = input_node.get('lifespan') or 0 > 0
    has_valid_value = _get_value(input_node, 'value') or 0 > 0
    has_depreciated_term = _has_depreciated_term(term)

    should_run = all([
        has_depreciated_term,
        has_valid_value,
        has_lifespan
    ])

    logRequirements(cycle, model=MODEL, term=term_id, model_key=MODEL_KEY,
                    has_valid_value=has_valid_value,
                    has_lifespan=has_lifespan,
                    has_depreciated_term=has_depreciated_term)
    logShouldRun(input_node, MODEL, term_id, should_run, model_key=MODEL_KEY)
    return should_run


def _should_run_infrastructure(cycle: dict, infra_node: dict) -> tuple[bool, list]:
    inputs = filter_list_term_type(infra_node.get('inputs', []), [TermTermType.MATERIAL, TermTermType.SUBSTRATE])
    inputs = [
        i | {
            'lifespan': i.get('lifespan') or infra_node.get('defaultLifespan')
        }
        for i in inputs
    ]
    return [i for i in inputs if _should_run_input(cycle, i)]


def _should_run(cycle: dict) -> tuple[bool, list]:
    inputs = flatten([
        _should_run_infrastructure(cycle, i)
        for i in cycle.get('site', {}).get('infrastructure', [])
    ])
    has_material_inputs = len(inputs) > 0
    cycle_duration = cycle.get('cycleDuration')
    is_incomplete = _is_term_type_incomplete(cycle, TermTermType.MATERIAL)

    logRequirements(cycle, model=MODEL, term=None, model_key=MODEL_KEY,
                    term_type_material_incomplete=is_incomplete,
                    has_material_inputs=has_material_inputs)

    should_run = all([is_incomplete, has_material_inputs, cycle_duration])
    logShouldRun(cycle, MODEL, None, should_run, model_key=MODEL_KEY)
    return should_run, inputs


def run(cycle: dict):
    should_run, inputs = _should_run(cycle)
    return [_run_input(cycle, i) for i in inputs] if should_run else []
