from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, flatten

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from . import MODEL
from ..utils.indicator import _new_indicator
from ..utils.lookup import _node_value

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [
            {
                "@type": "Indicator", "value": "", "term.termType": "resourceUse",
                "term.@id": ["resourceUseMineralsAndMetalsInputsProduction", "resourceUseMineralsAndMetalsDuringCycle"],
                "inputs": [{
                    "@type": "Term",
                    "term.units": "kg",
                    "term.termType": ["material", "soilAmendment", "otherInorganicChemical"]
                }]
            }]
    }
}

LOOKUPS = {
    "@doc": "Different lookup files are used depending on the input material",
    "soilAmendment": "abioticResourceDepletionMineralsAndMetalsCml2001Baseline",
    "material": "abioticResourceDepletionMineralsAndMetalsCml2001Baseline",
    "otherInorganicChemical": "abioticResourceDepletionMineralsAndMetalsCml2001Baseline"
}

RETURNS = {
    "Indicator": {
        "value": ""
    }
}

TERM_ID = 'abioticResourceDepletionMineralsAndMetals'

authorised_resource_use_term_types = [TermTermType.MATERIAL.value,
                                      TermTermType.SOILAMENDMENT.value,
                                      TermTermType.OTHERINORGANICCHEMICAL.value]
authorised_resource_use_term_ids = ['resourceUseMineralsAndMetalsInputsProduction',
                                    'resourceUseMineralsAndMetalsDuringCycle']


def _valid_input(input: dict) -> bool:
    return input.get('units', '').startswith("kg") and input.get('termType', '') in authorised_resource_use_term_types


def _valid_resource_indicator(resource: dict) -> bool:
    return len(resource.get('inputs', [])) == 1 and isinstance(_node_value(resource), (int, float))


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def _run(resources: list):
    result = list_sum([indicator_input['value'] * indicator_input['coefficient'] for indicator_input in resources])
    return _indicator(result)


def _should_run(impact_assessment: dict) -> tuple[bool, list]:
    emissions_resource_use = [
        resource for resource in
        filter_list_term_type(impact_assessment.get('emissionsResourceUse', []), TermTermType.RESOURCEUSE) if
        resource.get('term', {}).get('@id', '') in authorised_resource_use_term_ids]

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
                    "value": _node_value(resource_indicator),
                    "coefficient": get_table_value(
                        lookup=download_lookup(filename=f"{input.get('termType')}.csv"),
                        col_match='termid',
                        col_match_with=input.get('@id'),
                        col_val=column_name(LOOKUPS.get(input.get('termType'), ''))) if input else None
                } for input in resource_indicator['inputs'] or [{}]]
            for resource_indicator in emissions_resource_use
        ]
    )
    valid_resources_with_cf = [em for em in resource_uses_unpacked if em['coefficient'] is not None
                               and em['indicator-is-valid'] is True
                               and em['indicator-input-is-valid'] is True]

    has_valid_input_requirements = all([
        all([
            em['indicator-is-valid'],
            em['indicator-input-is-valid']
        ])
        for em in resource_uses_unpacked
    ])

    all_resources_have_cf = all([em['coefficient'] is not None for em in resource_uses_unpacked]
                                ) and bool(resource_uses_unpacked)

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    has_resource_use_entries=has_resource_use_entries,
                    has_valid_input_requirements=has_valid_input_requirements,
                    all_resources_have_cf=all_resources_have_cf,
                    resource_uses=log_as_table(resource_uses_unpacked)
                    )

    should_run = all([has_valid_input_requirements, has_resource_use_entries])

    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run, valid_resources_with_cf


def run(impact_assessment: dict):
    should_run, resources = _should_run(impact_assessment)
    return _run(resources) if should_run else None
