from functools import reduce
from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.inorganicFertiliser import (
    get_NH3_emission_factor, get_terms, get_term_lookup, get_country_breakdown, get_cycle_inputs
)
from hestia_earth.models.utils.constant import Units
from .utils import _emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
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
        ],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"},
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "soilPh"},
                {"@type": "Measurement", "value": "", "term.@id": "temperatureAnnual"}
            ]
        }
    }
}
LOOKUPS = {
    "inorganicFertiliser": ["NH3_emissions_factor_acidic", "NH3_emissions_factor_basic"],
    "region-inorganicFertiliser-fertGroupingNitrogen-breakdown": ""
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2"
    }]
}
TERM_ID = 'nh3ToAirInorganicFertiliser'
TIER = EmissionMethodTier.TIER_2.value
UNSPECIFIED_TERM_ID = 'inorganicNitrogenFertiliserUnspecifiedKgN'


def _input_with_factor(soilPh: float, temperature: float):
    def get_value(input: dict):
        term_id = input.get('term', {}).get('@id')
        factor = get_NH3_emission_factor(term_id, soilPh, temperature) if all([
            soilPh is not None,
            temperature is not None
        ]) else None
        value = list_sum(input.get('value'), None)
        return {'id': term_id, 'value': value, 'factor': factor} if all([
            value is not None,
            factor is not None
        ]) else None
    return get_value


def _get_groupings():
    term_ids = get_terms()

    def get_grouping(groupings: dict, term_id: str):
        grouping = get_term_lookup(term_id, 'fertGroupingNitrogen')
        return groupings | ({grouping: term_id} if len(grouping) > 0 else {})

    return reduce(get_grouping, term_ids, {})


def _unspecified_inputs_with_factor(temperature: float, soilPh: float, unspecifiedKgN_value: float, site: dict):
    country_id = site.get('country', {}).get('@id')
    # creates a dictionary grouping => term_id with only a single key per group (avoid counting twice)
    groupings = _get_groupings()
    breakdown_inputs = [(
        term_id, get_country_breakdown(MODEL, TERM_ID, country_id, grouping)
    ) for grouping, term_id in groupings.items()] if all([country_id, unspecifiedKgN_value is not None]) else []
    # create inputs from country breakdown
    N_inputs = [
        {
            'term': {'@id': term_id},
            'value': [value * unspecifiedKgN_value]
        }
        for term_id, value in breakdown_inputs if value is not None
    ]
    return non_empty_list(map(_input_with_factor(soilPh, temperature), N_inputs))


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    soilPh = most_relevant_measurement_value(measurements, 'soilPh', end_date)
    temperature = most_relevant_measurement_value(
        measurements, 'temperatureAnnual', end_date) or most_relevant_measurement_value(
        measurements, 'temperatureLongTermAnnualMean', end_date)

    N_inputs = _filter_list_term_unit(get_cycle_inputs(cycle), Units.KG_N)
    has_N_inputs = len(N_inputs) > 0

    N_inputs_with_factor = non_empty_list(map(_input_with_factor(soilPh, temperature), N_inputs))
    has_N_inputs_with_factor = len(N_inputs_with_factor) > 0

    # fallback using country averages of fertilisers usage
    unspecifiedKgN_value = list_sum(find_term_match(N_inputs, UNSPECIFIED_TERM_ID).get('value'), None)
    unspecified_inputs_with_factor = _unspecified_inputs_with_factor(temperature, soilPh, unspecifiedKgN_value, site)
    has_unspecified_inputs_with_factor = len(unspecified_inputs_with_factor) > 0

    fertiliser_complete = _is_term_type_complete(cycle, 'fertiliser')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_fertiliser_complete=fertiliser_complete,
                    temperature=temperature,
                    soilPh=soilPh,
                    has_N_inputs=has_N_inputs,
                    inorganic_fertiliser_inputs=log_as_table(N_inputs_with_factor),
                    unspecified_fertiliser_inputs=log_as_table(unspecified_inputs_with_factor))

    should_run = all([
        fertiliser_complete,
        temperature,
        soilPh,
        not has_N_inputs or has_N_inputs_with_factor or has_unspecified_inputs_with_factor
    ])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, N_inputs_with_factor or unspecified_inputs_with_factor


def run(cycle: dict):
    should_run, N_inputs_with_factor = _should_run(cycle)
    value = list_sum([i.get('value') * i.get('factor') for i in N_inputs_with_factor]) if should_run else None
    return [_emission(value=value, tier=TIER, term_id=TERM_ID)] if value is not None else []
