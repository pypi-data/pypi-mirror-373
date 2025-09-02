from typing import Optional
from functools import lru_cache
from hestia_earth.schema import SchemaType, SiteSiteType, TermTermType
from hestia_earth.utils.api import find_related
from hestia_earth.utils.tools import non_empty_list, flatten, safe_parse_date

from . import cached_value, _load_calculated_node
from .term import get_land_cover_siteTypes
from .lookup import get_region_lookup_value

CACHE_YEARS_KEY = 'years'
WATER_TYPES = [
    SiteSiteType.POND.value,
    SiteSiteType.RIVER_OR_STREAM.value,
    SiteSiteType.LAKE.value,
    SiteSiteType.SEA_OR_OCEAN.value
]
FRESH_WATER_TYPES = [
    SiteSiteType.RIVER_OR_STREAM.value,
    SiteSiteType.LAKE.value
]


def region_level_1_id(term_id: str):
    """
    Get the level 1 `@id` of the region.

    Parameters
    ----------
    term_id : str
        The `@id` of the region Term

    Returns
    -------
    str
        The `@id` of the `region` with a maximum level of 1.
    """
    term_parts = term_id.split('.') if term_id else []
    return None if term_id is None or not term_id.startswith('GADM') else (
        term_id if len(term_id) == 8 else (
            f"{'.'.join(term_parts[0:2])}{('_' + term_id.split('_')[1]) if len(term_parts) > 2 else ''}"
        )
    )


def _cycle_year(cycle: dict, key: str):
    date = safe_parse_date(cycle.get(key))
    return date.year if date else None


def years_from_cycles(cycles: list):
    """
    Get the list of years available for all cycles.

    Parameters
    ----------
    cycles : list
        List of Cycle as dict.

    Returns
    -------
    list[int]
        List of years available.
    """
    return sorted(non_empty_list(set(flatten([
        _cycle_year(cycle, 'startDate'),
        _cycle_year(cycle, 'endDate')
    ] for cycle in cycles))))


def related_cycles(site: dict, cycles_mapping: Optional[dict[str, dict]] = None):
    """
    Get the list of `Cycle` related to the `Site`.
    Gets the `recalculated` data if available, else `original`.

    Parameters
    ----------
    site_id : str
        The `@id` of the `Site`.
    cycles_mapping : dict[str, dict], optional
        An optional dict of related `Cycle`s for which the data has already been retrieved, with the format
        `{cycle_id (str): cycle (dict), ...ids}`.

    Returns
    -------
    list[dict]
        The related `Cycle`s as `dict`.
    """
    cycles_mapping = cycles_mapping or {}

    cached_nodes = [n for n in cached_value(site, 'related', []) if n.get('@type') == SchemaType.CYCLE.value]
    related_nodes = cached_nodes or find_related(SchemaType.SITE, site.get('@id'), SchemaType.CYCLE) or []
    return non_empty_list(map(
        lambda node: cycles_mapping.get(node['@id']) or _load_calculated_node(node, SchemaType.CYCLE),
        related_nodes
    ))


def related_years(site: dict):
    years = cached_value(site, CACHE_YEARS_KEY) or years_from_cycles(related_cycles(site))
    return sorted(years) if years else []


def related_months(site: dict):
    return cached_value(site)


def valid_site_type(site: dict, site_types=[SiteSiteType.CROPLAND.value, SiteSiteType.PERMANENT_PASTURE.value]):
    """
    Check if the site `siteType` is allowed.

    Parameters
    ----------
    site : dict
        The `Site`.
    site_types : list[string]
        List of valid site types. Defaults to `['cropland', 'permanent pasture']`.
        Full list available on https://hestia.earth/schema/Site#siteType.

    Returns
    -------
    bool
        `True` if `siteType` matches the allowed values, `False` otherwise.
    """
    site_type = site.get('siteType') if site is not None else None
    return site_type in site_types


def region_factor(model: str, region_id: str, term_id: str, termType: TermTermType):
    return get_region_lookup_value(f"region-{termType.value}.csv", region_id, term_id, model=model, term=term_id)


@lru_cache()
def get_land_cover_term_id(site_type: str):
    land_cover_terms = get_land_cover_siteTypes()
    term = next((
        term for term in land_cover_terms if term["name"].lower() == site_type.lower()
    ), {}) if site_type else {}
    return term.get('@id')
