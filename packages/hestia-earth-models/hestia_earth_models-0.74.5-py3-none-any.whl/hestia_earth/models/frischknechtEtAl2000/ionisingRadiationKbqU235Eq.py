from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import flatten, list_sum
from hestia_earth.utils.blank_node import group_by_keys

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils import unique_values, _omit, _include
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.lookup import _node_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{
            "@type": "Indicator",
            "value": "",
            "term.@id": [
                "ionisingCompoundsToAirInputsProduction",
                "ionisingCompoundsToWaterInputsProduction",
                "ionisingCompoundsToSaltwaterInputsProduction"
            ],
            "key": {"@type": "Term", "term.termType": "waste", "term.units": "kg"}
        }]
    }
}
LOOKUPS = {
    "waste": [
        "ionisingCompoundsToAirInputsProduction",
        "ionisingCompoundsToWaterInputsProduction",
        "ionisingCompoundsToSaltwaterInputsProduction"
    ]
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "key": "",
        "inputs": ""
    }]
}

TERM_ID = 'ionisingRadiationKbqU235Eq'


def _indicator(value: float, key: dict, inputs: list) -> dict:
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['key'] = key
    indicator['value'] = value
    if inputs:
        indicator['inputs'] = inputs
    return indicator


def _run(emissions: list) -> list[dict]:
    indicators = [
        _indicator(
            value=list_sum([emission['value'] * emission['coefficient'] for emission in emission_group]),
            key=emission_group[0]['key'],
            inputs=unique_values(flatten([emission.get('inputs', []) for emission in emission_group]))
        )
        for emission_group in group_by_keys(emissions, ['key']).values()
    ]

    return indicators


def _valid_key(term: dict) -> bool:
    return term.get('units', '').startswith("kg") and term.get('termType') == TermTermType.WASTE.value


def _should_run(impact_assessment: dict) -> tuple[bool, list]:
    emissions = [
        emission
        for emission in filter_list_term_type(impact_assessment.get('emissionsResourceUse', []), TermTermType.EMISSION)
        if emission.get('term', {}).get('@id', '') in LOOKUPS[TermTermType.WASTE.value]
    ]

    has_emissions = bool(emissions)

    emissions_unpacked = [
        {
            "key-term-id": emission['key'].get('@id'),
            "key-term-type": emission['key'].get('termType'),
            "key-is-valid": _valid_key(emission['key']),
            "indicator-term-id": emission['term']['@id'],
            "value": _node_value(emission),
            "coefficient": get_table_value(
                lookup=download_lookup(filename="waste.csv"),
                col_match='termid',
                col_match_with=emission['key'].get('@id'),
                col_val=column_name(emission['term']['@id'])
            )
        } | _include(emission, ['key', 'inputs'])
        for emission in emissions
        if emission.get('key')
    ]

    valid_emission_with_cf = [
        em for em in emissions_unpacked if all([
            em['coefficient'] is not None,
            em['key-is-valid'] is True
        ])
    ]

    valid_key_requirements = all([
        all([
            em['key-is-valid']
        ])
        for em in emissions_unpacked
    ])

    all_emissions_have_known_cf = all([
        em['coefficient'] is not None for em in emissions_unpacked
    ]) and bool(emissions_unpacked)

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    has_emissions=has_emissions,
                    valid_key_requirements=valid_key_requirements,
                    all_emissions_have_known_CF=all_emissions_have_known_cf,
                    emissions=log_as_table([_omit(v, ['key', 'inputs']) for v in emissions_unpacked])
                    )

    should_run = all([emissions_unpacked, valid_key_requirements])

    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run, valid_emission_with_cf


def run(impact_assessment: dict):
    should_run, emissions = _should_run(impact_assessment)
    return _run(emissions) if should_run else []
