from collections import defaultdict
from itertools import groupby
from typing import Tuple, Optional

from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils import Units, _include
from hestia_earth.models.utils.blank_node import convert_unit
from hestia_earth.models.utils.indicator import _new_indicator
from . import MODEL
from ..utils.lookup import _node_value

REQUIREMENTS = {
    "Cycle": {
        "inputs": [
            {
                "@type": "Input",
                "term.units": ["kg", "m3", "kWh", "MJ"],
                "term.termType": ["fuel", "electricity"],
                "value": ">0",
                "optional": {
                    "properties": [
                        {
                            "@type": "Property",
                            "value": "",
                            "term.@id": "energyContentLowerHeatingValue",
                            "term.units": "MJ / kg"
                        },
                        {
                            "@type": "Property",
                            "value": "",
                            "term.@id": "density",
                            "term.units": "kg / m3"
                        }
                    ]
                }
            }
        ]
    }
}

RETURNS = {
    "Indicator": [
        {
            "value": "",
            "inputs": ""
        }
    ]
}

LOOKUPS = {
    "fuel": ["energyContentLowerHeatingValue", "density"]
}

TERM_ID = 'resourceUseEnergyDepletionDuringCycle'

INPUTS_TYPES_UNITS = {
    TermTermType.FUEL.value: [Units.KG.value, Units.M3.value, Units.MJ.value],
    TermTermType.ELECTRICITY.value: [Units.KW_H.value, Units.MJ.value]
}


def _indicator(values: list[float], cycle_input: dict):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = list_sum(values)
    indicator['inputs'] = [cycle_input | {"units": "MJ"}]
    return indicator


def _run(grouped_energy_terms: dict):
    indicators = [_indicator(values=[input['value-in-MJ'] for input in energy_term_group_vals],
                             cycle_input=energy_term_group_vals[0]['input']['term'])
                  for energy_term_group_vals in grouped_energy_terms.values()]
    return indicators


def _valid_input(input: dict) -> bool:
    return (isinstance(_node_value(input), (int, float))
            and _node_value(input) > 0
            and input.get("term", {}).get("units", "") in INPUTS_TYPES_UNITS.get(input.get("term", {}).get("termType")))


def _get_value_in_mj(input: dict) -> Optional[float]:
    return convert_unit(input, dest_unit=Units.MJ, node_value=_node_value(input)) if _valid_input(input) else None


def _should_run(cycle: dict) -> Tuple[bool, dict]:
    energy_input_terms = filter_list_term_type(cycle.get('inputs', []), [TermTermType.FUEL, TermTermType.ELECTRICITY])

    has_energy_terms = bool(energy_input_terms)

    energy_input_terms_unpacked = [
        {
            "id": input.get('term', {}).get('@id'),
            "termType": input.get('term', {}).get('termType'),
            "input-is-valid": _valid_input(input),
            "value": _node_value(input),
            "input": input,
            "units": input.get('term', {}).get('units'),
            "value-in-MJ": _get_value_in_mj(input)
        }
        for input in energy_input_terms
    ]

    has_valid_input_requirements = all([energy_input['input-is-valid'] for energy_input in energy_input_terms_unpacked])

    energy_input_terms_valid = [e for e in energy_input_terms_unpacked if e["value-in-MJ"] is not None]

    energy_input_terms_in_mj = [energy_input['value-in-MJ'] for energy_input in energy_input_terms_unpacked]
    all_inputs_have_valid_mj_value = all([mj_value is not None for mj_value in energy_input_terms_in_mj]
                                         ) and bool(energy_input_terms_in_mj)

    grouped_energy_terms = defaultdict(list)
    for k, v in groupby(energy_input_terms_valid, key=lambda x: x.get('id')):
        grouped_energy_terms[k].extend(list(v))

    logs = [
        _include(input, ['id', 'units', 'termType', 'value', 'value-in-MJ']) | {
            'properties': "    ".join([
                f"{p.get('term', {}).get('@id')}= {p.get('value')} ({p.get('term', {}).get('units')})"
                for p in input.get('properties', [])
            ])
        } for input in energy_input_terms_unpacked
    ]
    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    has_energy_terms=has_energy_terms,
                    has_valid_input_requirements=has_valid_input_requirements,
                    all_inputs_have_valid_mj_value=all_inputs_have_valid_mj_value,
                    energy_resources_used=log_as_table(logs))

    should_run = all([has_valid_input_requirements, all_inputs_have_valid_mj_value])

    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run, grouped_energy_terms


def run(cycle: dict):
    should_run, grouped_energy_terms = _should_run(cycle)
    return _run(grouped_energy_terms) if should_run else []
