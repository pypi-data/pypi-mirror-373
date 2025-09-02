from statistics import mean
from hestia_earth.schema import EmissionMethodTier, TermTermType
from hestia_earth.utils.tools import flatten, list_sum
from hestia_earth.utils.blank_node import group_by_keys

from hestia_earth.models.log import logShouldRun, logRequirements
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.background_emissions import (
    get_background_inputs,
    no_gap_filled_background_emissions,
    log_missing_emissions,
    parse_term_id,
    process_input_mappings
)
from .utils import get_input_mappings, extract_input_mapping
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
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
    "ecoalim-emission": "emission-",
    "emission": "inputProductionGroupId",
    "animalProduct": "ecoalimMapping",
    "crop": "ecoalimMapping",
    "feedFoodAdditive": "ecoalimMapping",
    "forage": "ecoalimMapping",
    "processedFood": "ecoalimMapping"
}
MODEL_KEY = 'cycle'
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(term_id: str, value: float, input: dict, country_id: str = None, key_id: str = None):
    emission = _new_emission(term_id, MODEL, country_id, key_id)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['inputs'] = [input.get('term')]
    if input.get('operation'):
        emission['operation'] = input.get('operation')
    if input.get('animal'):
        emission['animals'] = [input.get('animal')]
    return emission


def _run_input(cycle: dict):
    no_gap_filled_background_emissions_func = no_gap_filled_background_emissions(cycle)
    log_missing_emissions_func = log_missing_emissions(cycle, model=MODEL, methodTier=TIER)

    def run(inputs: list):
        input = inputs[0]
        input_term_id = input.get('term', {}).get('@id')
        input_value = list_sum(flatten(input.get('value', []) for input in inputs))
        mappings = get_input_mappings(MODEL, input)
        has_mappings = len(mappings) > 0

        # grouping the inputs together in the logs
        input_parent_term_id = (input.get('parent', {})).get('@id') or input.get('animalId', {})
        extra_logs = {
            **({'input_group_id': input_parent_term_id} if input_parent_term_id else {}),
            **({'animalId': input.get('animalId')} if input.get('animalId') else {})
        }

        # skip input that has background emissions we have already gap-filled (model run before)
        has_no_gap_filled_background_emissions = no_gap_filled_background_emissions_func(input)

        logRequirements(cycle, model=MODEL, term=input_term_id, model_key=MODEL_KEY,
                        has_mappings=has_mappings,
                        mappings=';'.join([v[1] for v in mappings]),
                        has_no_gap_filled_background_emissions=has_no_gap_filled_background_emissions,
                        input_value=input_value,
                        **extra_logs)

        should_run = all([has_mappings, has_no_gap_filled_background_emissions, input_value])
        logShouldRun(cycle, MODEL, input_term_id, should_run, methodTier=TIER, model_key=MODEL_KEY, **extra_logs)

        results = process_input_mappings(
            cycle, input, mappings, TermTermType.EMISSION,
            extract_mapping=extract_input_mapping,
            **(
                extra_logs | {'model': MODEL, 'model_key': MODEL_KEY}
            )
        ) if should_run else {}
        log_missing_emissions_func(input_term_id, list(map(parse_term_id, results.keys())), **(
            extra_logs | {'has_mappings': has_mappings}
        ))
        return [
            _emission(
                term_id=parse_term_id(term_id),
                value=mean([v['value'] * v['coefficient'] for v in values]) * input_value,
                input=input,
                country_id=values[0].get('country'),
                key_id=values[0].get('key'),
            )
            for term_id, values in results.items()
        ]
    return run


def run(cycle: dict):
    inputs = get_background_inputs(cycle)
    grouped_inputs = group_by_keys(inputs, ['term', 'operation', 'animal'])
    return flatten(map(_run_input(cycle), grouped_inputs.values()))
