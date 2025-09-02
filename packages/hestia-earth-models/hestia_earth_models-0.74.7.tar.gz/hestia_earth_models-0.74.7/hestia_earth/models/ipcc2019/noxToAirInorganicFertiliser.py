from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues, log_as_table
from hestia_earth.models.utils.blank_node import get_N_total
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_inorganic_fertiliser_N_total
from hestia_earth.models.utils.term import get_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.termType": "inorganicFertiliser",
                "optional": {
                    "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
                }
            },
            {
                "@type": "Input",
                "value": "",
                "term.termType": "fertiliserBrandName",
                "properties": [{"@type": "Property", "value": "", "key.termType": "inorganicFertiliser"}]
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
        "methodModelDescription": ["Aggregated version", "Disaggragated version"]
    }]
}
LOOKUPS = {
    "inorganicFertiliser": ["IPCC_2019_FRACGASF_NOx-N", "IPCC_2019_FRACGASF_NOx-N-min", "IPCC_2019_FRACGASF_NOx-N-max"]
}
TERM_ID = 'noxToAirInorganicFertiliser'
TIER = EmissionMethodTier.TIER_1.value
TERM_TYPE = TermTermType.INORGANICFERTILISER
UNSPECIFIED_TERM_ID = 'inorganicNitrogenFertiliserUnspecifiedKgN'


def _emission(value: float, min: float, max: float, aggregated: bool = False):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['min'] = [min]
    emission['max'] = [max]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['methodModelDescription'] = 'Aggregated version' if aggregated else 'Disaggregated version'
    return emission


def _input_values(input: dict):
    N_total = list_sum(get_N_total([input]))
    lookups = LOOKUPS[TERM_TYPE.value]
    return {
        'id': input.get('term', {}).get('@id'),
        'N': N_total,
        'value': get_lookup_value(input.get('term', {}), lookups[0]),
        'min': get_lookup_value(input.get('term', {}), lookups[1]),
        'max': get_lookup_value(input.get('term', {}), lookups[2])
    }


def _filter_input_values(values: list, key: str): return [value for value in values if value.get(key)]


def _run(cycle: dict):
    inputs = filter_list_term_type(cycle.get('inputs', []), TERM_TYPE)
    input_values = list(map(_input_values, inputs))

    debugValues(cycle, model=MODEL, term=TERM_ID,
                input_values=log_as_table(input_values))

    value = list_sum([
        v.get('N', 0) * v.get('value', 0) for v in _filter_input_values(input_values, 'value')
    ]) * get_atomic_conversion(Units.KG_NOX, Units.TO_N)

    min = list_sum([
        v.get('N', 0) * v.get('min', 0) for v in _filter_input_values(input_values, 'min')
    ]) * get_atomic_conversion(Units.KG_NOX, Units.TO_N)

    max = list_sum([
        v.get('N', 0) * v.get('max', 0) for v in _filter_input_values(input_values, 'max')
    ]) * get_atomic_conversion(Units.KG_NOX, Units.TO_N)

    aggregated = list_sum(find_term_match(inputs, UNSPECIFIED_TERM_ID).get('value', [0])) > 0

    return [_emission(value, min, max, aggregated=aggregated)]


def _should_run(cycle: dict):
    N_inorganic_fertiliser = get_inorganic_fertiliser_N_total(cycle)
    fertiliser_complete = _is_term_type_complete(cycle, 'fertiliser')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_inorganic_fertiliser=N_inorganic_fertiliser,
                    term_type_fertiliser_complete=fertiliser_complete)

    should_run = all([N_inorganic_fertiliser is not None, fertiliser_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
