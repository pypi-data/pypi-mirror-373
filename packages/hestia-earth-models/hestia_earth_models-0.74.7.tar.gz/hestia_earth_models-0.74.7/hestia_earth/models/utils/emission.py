from collections.abc import Iterable
from typing import Optional, Union
from hestia_earth.schema import EmissionMethodTier, SchemaType, TermTermType
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.emission import cycle_emissions_in_system_boundary, emissions_in_system_boundary

from . import flatten_args
from .term import download_term
from .blank_node import find_terms_value
from .method import include_methodModel
from .constant import Units, get_atomic_conversion

EMISSION_METHOD_TIERS = [e.value for e in EmissionMethodTier]


def _new_emission(term, model=None, country_id: str = None, key_id: str = None):
    node = {'@type': SchemaType.EMISSION.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_term(term, TermTermType.EMISSION))
    if country_id:
        node['country'] = linked_node(download_term(country_id, TermTermType.REGION))
    if key_id:
        node['key'] = linked_node(download_term(key_id))
    return include_methodModel(node, model)


def get_nh3_no3_nox_to_n(cycle: dict, nh3_term_id: str = None, no3_term_id: str = None, nox_term_id: str = None):
    nh3 = find_terms_value(cycle.get('emissions', []), nh3_term_id, default=None)
    nh3 = None if nh3 is None else nh3 / get_atomic_conversion(Units.KG_NH3, Units.TO_N)
    no3 = find_terms_value(cycle.get('emissions', []), no3_term_id, default=None)
    no3 = None if no3 is None else no3 / get_atomic_conversion(Units.KG_NO3, Units.TO_N)
    nox = find_terms_value(cycle.get('emissions', []), nox_term_id, default=None)
    nox = None if nox is None else nox / get_atomic_conversion(Units.KG_NOX, Units.TO_N)

    return (nh3, no3, nox)


_EMISSION_METHOD_TIER_RANKING = [
    EmissionMethodTier.MEASURED,
    EmissionMethodTier.TIER_3,
    EmissionMethodTier.TIER_2,
    EmissionMethodTier.TIER_1,
    EmissionMethodTier.BACKGROUND,
    EmissionMethodTier.NOT_RELEVANT
]
"""
A ranking of `EmissionMethodTier`s from strongest to weakest.
"""


_EmissionMethodTiers = Union[EmissionMethodTier, str, Iterable[Union[EmissionMethodTier, str]]]
"""
A type alias for a single emission method tier, as either an EmissionMethodTier enum or string, or multiple emission
method tiers, as either an iterable of EmissionMethodTier enums or strings.
"""


def min_emission_method_tier(*methods: _EmissionMethodTiers) -> EmissionMethodTier:
    """
    Get the minimum ranking emission method tier from the provided methods.

    n.b., `max` function is used as weaker methods have higher indices.

    Parameters
    ----------
    *methods : EmissionMethodTier | str | Iterable[EmissionMethodTier] | Iterable[str]
        Emission method tiers or iterables of emission method tiers.

    Returns
    -------
    EmissionMethodTier
        The emission method tier method with the minimum ranking.
    """
    methods_ = [to_emission_method_tier(arg) for arg in flatten_args(methods)]
    return max(
        methods_,
        key=lambda method: _EMISSION_METHOD_TIER_RANKING.index(method),
        default=_EMISSION_METHOD_TIER_RANKING[-1]
    )


def to_emission_method_tier(method: Union[EmissionMethodTier, str]) -> Optional[EmissionMethodTier]:
    """
    Convert the input str to an `EmissionMethodTier` if possible.

    Parameters
    ----------
    method : EmissionMethodTier | str
        The emission method tier as either a `str` or `EmissionMethodTier`.

    Returns
    -------
    EmissionMethodTier | None
        The matching `EmissionMethodTier` or `None` if invalid string.
    """
    return (
        method if isinstance(method, EmissionMethodTier)
        else EmissionMethodTier(method) if method in EMISSION_METHOD_TIERS
        else None
    )


def filter_emission_inputs(emission: dict, term_type: TermTermType):
    inputs = emission.get('inputs', [])
    return [i for i in inputs if i.get('termType') == term_type.value]


def background_emissions_in_system_boundary(node: dict, term_type: TermTermType = TermTermType.EMISSION):
    term_ids = (
        cycle_emissions_in_system_boundary(node, term_type) if term_type == TermTermType.EMISSION else
        emissions_in_system_boundary(term_type)
    )
    return [id for id in term_ids if 'InputsProduction' in id]
