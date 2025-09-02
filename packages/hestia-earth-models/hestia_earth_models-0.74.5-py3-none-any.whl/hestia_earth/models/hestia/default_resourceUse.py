from hestia_earth.schema import IndicatorMethodTier, TermTermType
from hestia_earth.utils.tools import flatten, safe_parse_float

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues
from hestia_earth.models.utils import _omit
from hestia_earth.models.utils.emission import background_emissions_in_system_boundary
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.background_emissions import no_gap_filled_background_emissions
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.input import unique_background_inputs
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "inputs": [{
                "@type": "Input",
                "value": "> 0",
                "none": {
                    "impactAssessment": {"@type": "ImpactAssessment"},
                    "fromCycle": "True",
                    "producedInCycle": "True"
                }
            }]
        }
    }
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "inputs": "",
        "methodTier": "background"
    }]
}
LOOKUPS = {
    "resourceUse": "inHestiaDefaultSystemBoundary",
    "organicFertiliser": "backgroundEmissionsResourceUseDefaultValue"
}
MODEL_KEY = 'default_resourceUse'
TIER = IndicatorMethodTier.BACKGROUND.value


def _indicator(term_id: str, value: float, input: dict):
    indicator = _new_indicator(term_id, MODEL)
    indicator['value'] = value
    indicator['inputs'] = [input]
    indicator['methodTier'] = TIER
    return indicator


def _default_value(input: dict):
    return safe_parse_float(get_lookup_value(input.get('term', {}), LOOKUPS['organicFertiliser']), default=None)


def _run_input(impact: dict):
    required_resourceUse_term_ids = background_emissions_in_system_boundary(impact, TermTermType.RESOURCEUSE)

    def run(input: dict):
        input_term = input.get('input').get('term')
        term_id = input_term.get('@id')
        value = input.get('default-value-from-lookup')

        for emission_id in required_resourceUse_term_ids:
            logShouldRun(impact, MODEL, term_id, True, methodTier=TIER, model_key=MODEL_KEY, emission_id=emission_id)
            debugValues(impact, model=MODEL, term=emission_id,
                        value=value,
                        coefficient=1,
                        input=term_id)

        return [
            _indicator(term_id, value, input_term) for term_id in required_resourceUse_term_ids
        ]

    return run


def _should_run(impact: dict):
    no_gap_filled_background_emissions_func = no_gap_filled_background_emissions(
        node=impact, list_key='emissionsResourceUse', term_type=TermTermType.RESOURCEUSE
    )

    inputs = [
        input | {
            'default-value-from-lookup': _default_value(input['input']),
            'no-gap-filled-background-emissions': no_gap_filled_background_emissions_func(input['input'])
        }
        for input in unique_background_inputs(impact.get('cycle', {}))
    ]
    valid_inputs = [
        input for input in inputs
        if all([
            input.get('default-value-from-lookup') is not None,
            input.get('no-gap-filled-background-emissions')
        ])
    ]

    should_run = all([bool(valid_inputs)])

    for input in inputs:
        term_id = input.get('input').get('term', {}).get('@id')

        logRequirements(impact, model=MODEL, term=term_id, model_key=MODEL_KEY,
                        **_omit(input, ['input', 'input-value']))
        logShouldRun(impact, MODEL, term_id, should_run, methodTier=TIER, model_key=MODEL_KEY)

    return should_run, valid_inputs


def run(impact: dict):
    should_run, grouped_inputs = _should_run(impact)
    return flatten(map(_run_input(impact), grouped_inputs)) if should_run else []
