from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import download_lookup, extract_grouped_data, lookup_term_ids
from hestia_earth.utils.tools import safe_parse_float
from hestia_earth.utils.model import filter_list_term_type

from .term import get_lookup_value
from .fertiliser import get_fertilisers_from_inputs
from .lookup import get_region_lookup_value

BREAKDOWN_LOOKUP = 'region-inorganicFertiliser-fertGroupingNitrogen-breakdown.csv'


def get_terms():
    lookup = download_lookup('inorganicFertiliser.csv', True)
    return lookup_term_ids(lookup)


def get_term_lookup(term_id: str, col_name: str):
    return get_lookup_value({'@id': term_id, 'termType': TermTermType.INORGANICFERTILISER.value}, col_name)


def _get_temperature_lookup_key(temperature: float):
    return 'cool' if temperature <= 14 else ('temperate' if temperature < 26 else 'warm')


def _get_soilPh_lookup_key(soilPh: float):
    return 'acidic' if soilPh <= 7 else 'basic'


def get_NH3_emission_factor(term_id: str, soilPh: float, temperature: float):
    soilPh_key = _get_soilPh_lookup_key(soilPh)
    temperature_key = _get_temperature_lookup_key(temperature)
    data = get_term_lookup(term_id, f"NH3_emissions_factor_{soilPh_key}")
    return safe_parse_float(extract_grouped_data(data, temperature_key), default=None)


def get_country_breakdown(model: str, term_id: str, country_id: str, col_name: str):
    value = get_region_lookup_value(BREAKDOWN_LOOKUP, country_id, col_name, model=model, term=term_id)
    return safe_parse_float(value, default=None)


def get_cycle_inputs(cycle: dict):
    return filter_list_term_type(cycle.get('inputs', []), TermTermType.INORGANICFERTILISER) + \
        get_fertilisers_from_inputs(cycle, TermTermType.INORGANICFERTILISER)
