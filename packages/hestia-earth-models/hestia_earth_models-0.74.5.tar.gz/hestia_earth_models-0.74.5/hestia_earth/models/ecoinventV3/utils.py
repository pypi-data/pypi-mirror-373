from functools import lru_cache
from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import column_name, load_lookup
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.data.ecoinventV3 import get_filepath
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.background_emissions import convert_background_lookup

_LOOKUP_INDEX_KEY = column_name('ecoinventName')


def get_input_mappings(model: str, input: dict):
    term = input.get('term', {})
    term_id = term.get('@id')
    value = get_lookup_value(term, 'ecoinventMapping', model=model, term=term_id)
    mappings = non_empty_list(value.split(';')) if value else []
    return [(m.split(':')[0], float(m.split(':')[1])) for m in mappings]


def extract_input_mapping(mapping: tuple, term_type: TermTermType):
    mapping_name, coefficient = mapping
    values = ecoinvent_values(mapping_name, term_type)
    return values, coefficient


@lru_cache()
def _build_lookup(term_type: str):
    filepath = get_filepath(term_type)

    lookup = load_lookup(filepath=filepath, keep_in_memory=False)
    return convert_background_lookup(lookup=lookup, index_column=_LOOKUP_INDEX_KEY)


@lru_cache()
def ecoinvent_values(mapping: str, term_type: TermTermType):
    data = _build_lookup(term_type.value)
    return list(data.get(mapping, {}).items())
