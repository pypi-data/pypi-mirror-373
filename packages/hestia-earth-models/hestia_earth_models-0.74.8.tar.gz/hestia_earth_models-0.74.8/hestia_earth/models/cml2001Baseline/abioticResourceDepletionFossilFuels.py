from itertools import chain
from hestia_earth.utils.lookup import download_lookup, column_name, find_term_ids_by
from hestia_earth.utils.tools import list_sum, flatten

from hestia_earth.models.log import logShouldRun, logRequirements, log_as_table
from . import MODEL
from ..utils.constant import Units
from ..utils.indicator import _new_indicator
from ..utils.lookup import _node_value

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [
            {
                "@type": "Indicator",
                "term.termType": "resourceUse",
                "term.@id": ["resourceUseEnergyDepletionInputsProduction", "resourceUseEnergyDepletionDuringCycle"],
                "term.units": "MJ",
                "value": "> 0",
                "inputs": [
                    {
                        "@type": "Input",
                        "term.name": "non-renewable\" energy terms only,\"",
                        "term.termType": ["fuel", "electricity"]
                    }
                ]
            }
        ]
    }
}

LOOKUPS = {
    "fuel": ["consideredFossilFuelUnderCml2001Baseline"],
    "electricity": ["consideredFossilFuelUnderCml2001Baseline"]
}

RETURNS = {
    "Indicator": {
        "value": ""
    }
}
TERM_ID = 'abioticResourceDepletionFossilFuels'

_ENERGY_CARRIERS_TERMIDS = REQUIREMENTS['ImpactAssessment']['emissionsResourceUse'][0]['term.@id']


def get_all_non_renewable_terms(lookup_file_name: str, column: str) -> list:
    """
    returns all non renewable term ids in lookup files like `electricity.csv` or `fuel.csv`
    """
    lookup = download_lookup(lookup_file_name)
    return find_term_ids_by(lookup, column_name(column), True)


def _valid_resource_indicator(resource: dict) -> bool:
    return (
        len(resource.get('inputs', [])) == 1 and
        isinstance(_node_value(resource), (int, float)) and
        _node_value(resource) > 0 and
        resource.get("term", {}).get("units", "") == Units.MJ.value
    )


def _valid_input(input: dict) -> bool:
    return input.get("@id") in list(chain.from_iterable([
        get_all_non_renewable_terms(f"{termType}.csv", columns[0]) for termType, columns in LOOKUPS.items()
    ]))


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator["value"] = value
    return indicator


def _run(energy_resources_in_mj: list):
    return _indicator(list_sum(energy_resources_in_mj))


def _should_run(impact_assessment: dict) -> tuple[bool, list]:
    emissions_resource_use = [
        resource for resource in impact_assessment.get('emissionsResourceUse', [])
        if resource.get('term', {}).get('@id') in _ENERGY_CARRIERS_TERMIDS
    ]

    has_resource_use_entries = bool(emissions_resource_use)

    resource_uses_unpacked = flatten(
        [
            [
                {
                    "input-term-id": input.get('@id'),
                    "input-term-type": input.get('termType'),
                    "indicator-term-id": resource_indicator['term']['@id'],
                    "indicator-is-valid": _valid_resource_indicator(resource_indicator),
                    "indicator-input-is-valid": _valid_input(input),
                    "value-in-MJ": _node_value(resource_indicator) if _valid_input(input) else None,
                } for input in resource_indicator['inputs'] or [{}]]
            for resource_indicator in emissions_resource_use
        ]
    )

    has_valid_input_requirements = all([
        all([energy_input['indicator-is-valid'], energy_input['indicator-input-is-valid']])
        for energy_input in resource_uses_unpacked
    ])

    energy_resources_in_mj = [energy_input['value-in-MJ'] for energy_input in resource_uses_unpacked]
    valid_energy_resources_in_mj = [value for value in energy_resources_in_mj if value is not None]
    all_inputs_have_valid_mj_value = all(
        [energy is not None for energy in energy_resources_in_mj] + [bool(energy_resources_in_mj)]
    )

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    has_resource_use_entries=has_resource_use_entries,
                    has_valid_input_requirements=has_valid_input_requirements,
                    all_inputs_have_valid_mj_value=all_inputs_have_valid_mj_value,
                    energy_resources_used=log_as_table(resource_uses_unpacked))

    should_run = all([has_resource_use_entries, has_valid_input_requirements, all_inputs_have_valid_mj_value])

    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run, valid_energy_resources_in_mj


def run(impact_assessment: dict):
    should_run, resources = _should_run(impact_assessment)
    return _run(resources) if should_run else None
