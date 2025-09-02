from functools import lru_cache
from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import download_lookup, column_name
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.background_emissions import convert_background_lookup

_LOOKUP_INDEX_KEY = column_name('ecoalimMappingName')


def get_input_mappings(model: str, input: dict):
    term = input.get('term', {})
    term_id = term.get('@id')
    value = get_lookup_value(term, 'ecoalimMapping', model=model, term=term_id)
    mappings = non_empty_list(value.split(';')) if value else []
    return [(m.split(':')[0], m.split(':')[1]) for m in mappings]


def extract_input_mapping(mapping: tuple, term_type: TermTermType):
    gadm_id, mapping_name = mapping
    # # all countries have the same coefficient
    coefficient = 1
    values = ecoalim_values(mapping_name, term_type)
    return values, coefficient


@lru_cache()
def _build_lookup(term_type: str):
    lookup = download_lookup(f"ecoalim-{term_type}.csv", keep_in_memory=False)
    return convert_background_lookup(lookup=lookup, index_column=_LOOKUP_INDEX_KEY)


@lru_cache()
def ecoalim_values(mapping: str, term_type: TermTermType):
    data = _build_lookup(term_type.value)
    return list(data[mapping].items())
