from functools import reduce
from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import flatten, list_sum
from hestia_earth.utils.blank_node import group_by_keys

from hestia_earth.models.log import logShouldRun, debugValues, log_as_table
from hestia_earth.models.utils import _include
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import load_impacts
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "value": "> 0",
            "impactAssessment": {
                "@type": "ImpactAssessment",
                "emissionsResourceUse": [{"@type": "Indicator", "value": ""}]
            }
        }],
        "optional": {
            "animals": [{
                "@type": "Animal",
                "inputs": [{
                    "@type": "Input",
                    "value": "> 0",
                    "impactAssessment": {
                        "@type": "ImpactAssessment",
                        "emissionsResourceUse": [{"@type": "Indicator", "value": ""}]
                    }
                }]
            }]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "background",
        "inputs": "",
        "operation": "",
        "animals": ""
    }]
}
LOOKUPS = {
    "emission": "inputProductionGroupId"
}
MODEL_KEY = 'emissions'
MODEL_AGGREGATED = 'hestiaAggregatedData'
TIER = EmissionMethodTier.BACKGROUND.value
_GROUP_BY_KEYS = ['term', 'key', 'operation', 'animal']


def _emission(model: str, term_id: str, value: float, input: dict, animal={}, extra={}):
    emission = _new_emission(term_id, model)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['inputs'] = [input]
    if animal:
        emission['animals'] = [animal]
    return emission | extra


def _run_emission(cycle: dict, emission_term_id: str, data: dict):
    def run_input(values: dict):
        value = values.get('value', 0)
        input_term = values.get('term', {})
        input_term_id = input_term.get('@id')
        key = values.get('key', {})
        operation = values.get('operation', {})
        animal = values.get('animal', {})
        is_aggregated = any(values.get('aggregated', []))
        model = MODEL_AGGREGATED if is_aggregated else MODEL

        logShouldRun(cycle, model, input_term_id, True, methodTier=TIER)

        # log run on each emission so we know it did run
        details = values.get('details', {})
        logShouldRun(cycle, MODEL, input_term_id, True, methodTier=TIER, emission_id=emission_term_id)
        debugValues(cycle, model=model, term=emission_term_id,
                    value=value,
                    coefficient=1,
                    details=log_as_table([{'impact-assessment-id': key} | value for key, value in details.items()]),
                    input=input_term_id,
                    key=key.get('@id'),
                    operation=operation.get('@id'),
                    animal=animal.get('@id'))

        return _emission(
            model=model,
            term_id=emission_term_id,
            value=value,
            input=input_term,
            animal=animal,
            extra=_include(values, ['key', 'operation'])
        )

    return list(map(run_input, data.values()))


def _emission_group(term_id: str):
    lookup = download_lookup('emission.csv', True)
    return get_table_value(lookup, 'termid', term_id, column_name('inputProductionGroupId'))


def _group_emissions(impact: dict):
    def _group_by(group: dict, emission: dict):
        term_id = emission.get('term', {}).get('@id')
        grouping = _emission_group(term_id)
        value = emission.get('value') or 0
        if grouping:
            group[grouping] = group.get(grouping, 0) + value
        return group

    emissions = impact.get('emissionsResourceUse', [])
    return reduce(_group_by, emissions, {})


def _animal_inputs(animal: dict):
    inputs = load_impacts(animal.get('inputs', []))
    return [(input | {'animal': animal.get('term', {})}) for input in inputs]


def _group_input_emissions(input: dict):
    impact = input.get('impactAssessment')
    emissions = _group_emissions(impact)
    return input | {'emissions': emissions}


def _group_inputs(group: dict, values: tuple):
    # input_group_key = 'group-id'
    # inputs = [{'term': {}, 'value':[], 'impactAssessment': {}, 'emissions': {'co2ToAirInputsProduction': 10}}]
    input_group_key, inputs = values
    for input in inputs:
        input_value = list_sum(input.get('value'))
        emissions = input.get('emissions', {})
        for emission_term_id, emission_value in emissions.items():
            group[emission_term_id] = group.get(emission_term_id, {})

            grouped_inputs = (
                group[emission_term_id].get(input_group_key) or
                _include(input, _GROUP_BY_KEYS) | {
                    'value': 0,
                    'aggregated': [],
                    'details': {}
                }
            )
            grouped_inputs['aggregated'].append(input.get('impactAssessment', {}).get('agregated', False))
            grouped_inputs['value'] = grouped_inputs['value'] + (emission_value * input_value)
            # for logging
            grouped_inputs['details'][input.get('impactAssessment', {}).get('@id')] = {
                'emission-value': emission_value,
                'input-value': input_value
            }
            group[emission_term_id][input_group_key] = grouped_inputs
    return group


def run(cycle: dict):
    inputs = flatten(
        load_impacts(cycle.get('inputs', [])) +
        list(map(_animal_inputs, cycle.get('animals', [])))
    )
    inputs = [i for i in inputs if list_sum(i.get('value', [])) > 0]

    # group inputs with same term/key/operation/animal to avoid adding emissions twice
    # inputs = {'group-id': [{'term': {},'value':[10],'impactAssessment': {}}]}
    inputs = group_by_keys(inputs, _GROUP_BY_KEYS)
    inputs = {key: list(map(_group_input_emissions, value)) for key, value in inputs.items()}

    # finally group everything by emission so we can log inputs together
    # emissions = {'co2ToAirInputsProduct': {'group-id':{'term':{},'value':10,'details':{}}}}
    emissions = reduce(_group_inputs, inputs.items(), {})

    return flatten([_run_emission(cycle, term_id, data) for term_id, data in emissions.items()])
