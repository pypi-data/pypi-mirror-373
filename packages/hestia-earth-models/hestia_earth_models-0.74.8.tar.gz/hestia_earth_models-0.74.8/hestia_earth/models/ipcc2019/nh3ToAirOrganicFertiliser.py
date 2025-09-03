from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues, log_as_table
from hestia_earth.models.utils.blank_node import get_N_total
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_organic_fertiliser_N_total
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.organicFertiliser import get_cycle_inputs as get_organicFertiliser_inputs
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.termType": "organicFertiliser",
                "optional": {
                    "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
                }
            },
            {
                "@type": "Input",
                "value": "",
                "term.termType": "fertiliserBrandName",
                "properties": [{"@type": "Property", "value": "", "key.termType": "organicFertiliser"}]
            }
        ]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled",
        "methodModelDescription": "Aggregated version"
    }]
}
LOOKUPS = {
    "organicFertiliser": ["IPCC_2019_FRACGASM_NH3-N", "IPCC_2019_FRACGASM_NH3-N-min", "IPCC_2019_FRACGASM_NH3-N-max"]
}
TERM_ID = 'nh3ToAirOrganicFertiliser'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float, min: float, max: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['min'] = [min]
    emission['max'] = [max]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['methodModelDescription'] = 'Aggregated version'
    return emission


def _input_values(input: dict):
    N_total = list_sum(get_N_total([input]))
    return {
        'id': input.get('term', {}).get('@id'),
        'N': N_total,
        'value': get_lookup_value(input.get('term', {}), LOOKUPS['organicFertiliser'][0]),
        'min': get_lookup_value(input.get('term', {}), LOOKUPS['organicFertiliser'][1]),
        'max': get_lookup_value(input.get('term', {}), LOOKUPS['organicFertiliser'][2])
    }


def _filter_input_values(values: list, key: str): return [value for value in values if value.get(key)]


def _run(cycle: dict):
    inputs = get_organicFertiliser_inputs(cycle)
    input_values = list(map(_input_values, inputs))

    debugValues(cycle, model=MODEL, term=TERM_ID,
                input_values=log_as_table(input_values))

    value = list_sum([
        v.get('N', 0) * v.get('value', 0) for v in _filter_input_values(input_values, 'value')
    ]) * get_atomic_conversion(Units.KG_NH3, Units.TO_N)

    min = list_sum([
        v.get('N', 0) * v.get('min', 0) for v in _filter_input_values(input_values, 'min')
    ]) * get_atomic_conversion(Units.KG_NH3, Units.TO_N)

    max = list_sum([
        v.get('N', 0) * v.get('max', 0) for v in _filter_input_values(input_values, 'max')
    ]) * get_atomic_conversion(Units.KG_NH3, Units.TO_N)

    return [_emission(value, min, max)]


def _should_run(cycle: dict):
    N_organic_fertiliser = get_organic_fertiliser_N_total(cycle)
    fertiliser_complete = _is_term_type_complete(cycle, 'fertiliser')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_organic_fertiliser=N_organic_fertiliser,
                    term_type_fertiliser_complete=fertiliser_complete)

    should_run = all([N_organic_fertiliser is not None, fertiliser_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
