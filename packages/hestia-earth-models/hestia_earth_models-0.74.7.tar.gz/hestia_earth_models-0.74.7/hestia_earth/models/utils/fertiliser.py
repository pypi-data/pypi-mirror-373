from typing import Union, List
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import flatten

from .blank_node import get_inputs_from_properties

_TERM_TYPES = [
    TermTermType.INORGANICFERTILISER,
    TermTermType.ORGANICFERTILISER,
    TermTermType.OTHERINORGANICCHEMICAL,
    TermTermType.OTHERORGANICCHEMICAL,
    TermTermType.PESTICIDEAI
]


def get_fertilisers_from_inputs(cycle: dict, term_types: Union[TermTermType, List[TermTermType]] = _TERM_TYPES):
    inputs = flatten(cycle.get('inputs', []) + [a.get('inputs', []) for a in cycle.get('animals', [])])
    inputs = filter_list_term_type(inputs, TermTermType.FERTILISERBRANDNAME)
    return flatten([get_inputs_from_properties(i, term_types) for i in inputs])
