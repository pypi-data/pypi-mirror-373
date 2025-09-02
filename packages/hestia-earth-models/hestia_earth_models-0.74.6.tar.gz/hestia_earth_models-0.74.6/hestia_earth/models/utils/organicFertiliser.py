from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type

from .fertiliser import get_fertilisers_from_inputs


def get_cycle_inputs(cycle: dict):
    return filter_list_term_type(cycle.get('inputs', []), TermTermType.ORGANICFERTILISER) + \
        get_fertilisers_from_inputs(cycle, TermTermType.ORGANICFERTILISER)
