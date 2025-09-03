from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import list_sum, safe_parse_float, non_empty_list
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils import multiply_values
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.term import get_urea_terms
from hestia_earth.models.utils.inorganicFertiliser import get_country_breakdown, get_term_lookup
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "",
        "inputs": [{"@type": "Input", "value": "", "term.termType": "inorganicFertiliser"}]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
LOOKUPS = {
    "inorganicFertiliser": ["Urea_UAS_Amm_Bicarb", "UAN_Solu", "CO2_urea_emissions_factor"]
}
TERM_ID = 'co2ToAirUreaHydrolysis'
TIER = EmissionMethodTier.TIER_1.value
UNSPECIFIED_TERM_ID = 'inorganicNitrogenFertiliserUnspecifiedKgN'


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _urea_emission_factor(term_id: str):
    return safe_parse_float(get_term_lookup(term_id, LOOKUPS['inorganicFertiliser'][2]), default=None)


def _run(urea_values: list):
    value = list_sum([v.get('value') * v.get('factor') for v in urea_values if v.get('value')])
    return [_emission(value)]


def _get_urea_value(cycle: dict, inputs: list, term_id: str):
    inputs = list(filter(lambda i: i.get('term', {}).get('@id') == term_id, inputs))
    values = [list_sum(i.get('value'), 0) for i in inputs if len(i.get('value', [])) > 0]
    return list_sum(values, default=None)


def _should_run(cycle: dict):
    is_fertiliser_complete = _is_term_type_complete(cycle, 'fertiliser')
    inputs = cycle.get('inputs', [])
    term_ids = get_urea_terms()

    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    urea_share = get_country_breakdown(MODEL, TERM_ID, country_id, LOOKUPS['inorganicFertiliser'][0])
    uan_share = get_country_breakdown(MODEL, TERM_ID, country_id, LOOKUPS['inorganicFertiliser'][1])
    urea_unspecified_as_n = list_sum(find_term_match(inputs, UNSPECIFIED_TERM_ID).get('value', []), default=None)

    urea_values = [
        {
            'id': term_id,
            'value': _get_urea_value(cycle, inputs, term_id),
            'factor': _urea_emission_factor(term_id)
        } for term_id in term_ids
    ] + non_empty_list([
        {
            'id': 'ureaKgN',
            'value': multiply_values([urea_unspecified_as_n, urea_share]),
            'factor': _urea_emission_factor('ureaKgN')
        },
        {
            'id': 'ureaAmmoniumNitrateKgN',
            'value': multiply_values([urea_unspecified_as_n, uan_share]),
            'factor': _urea_emission_factor('ureaAmmoniumNitrateKgN')
        }
    ] if urea_unspecified_as_n is not None else [])

    has_urea_value = any([data.get('value') is not None for data in urea_values])

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    is_term_type_fertiliser_complete=is_fertiliser_complete,
                    has_urea_value=has_urea_value,
                    urea_values=log_as_table(urea_values),
                    urea_unspecified_as_n=urea_unspecified_as_n,
                    urea_share=urea_share,
                    uan_share=uan_share)

    should_run = has_urea_value or is_fertiliser_complete
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, urea_values


def run(cycle: dict):
    should_run, urea_values = _should_run(cycle)
    return _run(urea_values) if should_run else []
