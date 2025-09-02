from functools import reduce
from hestia_earth.utils.tools import list_sum, flatten
from hestia_earth.schema import EmissionMethodTier, TermTermType
from hestia_earth.utils.blank_node import group_by_keys

from hestia_earth.models.log import logShouldRun, logRequirements, debugValues
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.background_emissions import get_background_inputs, no_gap_filled_background_emissions
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.term import get_electricity_grid_mix_terms
from .utils import get_input_coefficient
from ..ecoinventV3.utils import get_input_mappings, ecoinvent_values
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.electricityFuel": "True",
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"}
        },
        "inputs": [{
            "@type": "Input",
            "term.@id": ["electricityGridMarketMix", "electricityGridRenewableMix"],
            "value": "> 0",
            "none": {
                "fromCycle": "True",
                "producedInCycle": "True"
            }
        }],
        "optional": {
            "animals": [{
                "@type": "Animal",
                "inputs": [{
                    "@type": "Input",
                    "term.@id": ["electricityGridMarketMix", "electricityGridRenewableMix"],
                    "value": "> 0",
                    "none": {
                        "fromCycle": "True",
                        "producedInCycle": "True"
                    }
                }]
            }]
        }
    }
}
RETURNS = {
    "Emission": [{
        "term": "",
        "value": "",
        "methodTier": "background",
        "inputs": "",
        "operation": "",
        "animals": ""
    }]
}
LOOKUPS = {
    "emission": "inputProductionGroupId",
    "electricity": "ecoinventMapping",
    "region-ember-energySources": "",
    "ember-ecoinvent-mapping": ["ember", "ecoinventId", "ecoinventName"]
}

MODEL_KEY = 'cycle'
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(term_id: str, value: float, input: dict):
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['inputs'] = [input.get('term')]
    if input.get('operation'):
        emission['operation'] = input.get('operation')
    if input.get('animal'):
        emission['animals'] = [input.get('animal')]
    return emission


def _add_emission(cycle: dict, input: dict):
    input_term_id = input.get('term', {}).get('@id')
    operation_term_id = input.get('operation', {}).get('@id')
    animal_term_id = input.get('animal', {}).get('@id')
    # TODO: as inputs are grouped, there could be more than 1 country
    country_id = input.get('country', cycle.get('site', {}).get('country', {})).get('@id')

    def add(prev: dict, mapping: tuple):
        ecoinventName, _coefficient = mapping
        # recalculate the coefficient using the country and year if it should be included
        coefficient = get_input_coefficient(MODEL, cycle, country_id, ecoinventName) if _coefficient > 0 else 0
        emissions = ecoinvent_values(ecoinventName, TermTermType.EMISSION)
        for emission_term_id, data in emissions:
            # log run on each emission so we know it did run
            logShouldRun(cycle, MODEL, input_term_id, True, methodTier=TIER, emission_id=emission_term_id)
            debugValues(cycle, model=MODEL, term=emission_term_id,
                        value=data.get('value'),
                        coefficient=coefficient,
                        input=input_term_id,
                        operation=operation_term_id,
                        animal=animal_term_id)
            prev[emission_term_id] = prev.get(emission_term_id, 0) + (data.get('value') * coefficient)
        return prev
    return add


def _run_input(cycle: dict):
    electricity_complete = _is_term_type_complete(cycle, 'electricityFuel')
    no_gap_filled_background_emissions_func = no_gap_filled_background_emissions(cycle)

    def run(inputs: list):
        input = inputs[0]
        input_value = list_sum(flatten(input.get('value', []) for input in inputs))
        input_term_id = input.get('term', {}).get('@id')
        mappings = get_input_mappings(MODEL, input)
        has_mappings = len(mappings) > 0

        # skip input that has background emissions we have already gap-filled (model run before)
        has_no_gap_filled_background_emissions = no_gap_filled_background_emissions_func(input)

        logRequirements(cycle, model=MODEL, term=input_term_id,
                        has_ecoinvent_mappings=has_mappings,
                        ecoinvent_mappings=';'.join([v[0] for v in mappings]),
                        has_no_gap_filled_background_emissions=has_no_gap_filled_background_emissions,
                        termType_electricityFuel_complete=electricity_complete,
                        input_value=input_value)

        should_run = all([electricity_complete, has_mappings, has_no_gap_filled_background_emissions, input_value])
        logShouldRun(cycle, MODEL, input_term_id, should_run, methodTier=TIER)

        grouped_emissions = reduce(_add_emission(cycle, input), mappings, {}) if should_run else {}
        return [
            _emission(term_id, value * input_value, input)
            for term_id, value in grouped_emissions.items()
        ]
    return run


def run(cycle: dict):
    terms = get_electricity_grid_mix_terms()
    inputs = get_background_inputs(cycle)
    # only keep the inputs matching the grid terms
    inputs = [i for i in inputs if i.get('term', {}).get('@id') in terms]
    grouped_inputs = group_by_keys(inputs, ['term', 'operation', 'animal'])
    return flatten(map(_run_input(cycle), grouped_inputs.values()))
