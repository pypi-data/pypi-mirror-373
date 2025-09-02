from hestia_earth.schema import TermTermType, SiteSiteType
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import safe_parse_float

from .term import get_lookup_value
from .site import valid_site_type as site_valid_site_type

FAO_LOOKUP_COLUMN = 'cropGroupingFAO'
FAOSTAT_AREA_LOOKUP_COLUMN = 'cropGroupingFaostatArea'
FAOSTAT_PRODUCTION_LOOKUP_COLUMN = 'cropGroupingFaostatProduction'


def get_crop_lookup_value(model: str, log_id: str, term_id: str, column: str):
    return get_lookup_value({'@id': term_id, 'termType': TermTermType.CROP.value}, column, model=model, term=log_id)


def get_crop_grouping_fao(model: str, log_id: str, term: dict):
    return get_crop_lookup_value(model, log_id, term.get('@id'), FAO_LOOKUP_COLUMN)


def get_crop_grouping_faostat_area(model: str, log_id: str, term: dict):
    return get_crop_lookup_value(model, log_id, term.get('@id'), FAOSTAT_AREA_LOOKUP_COLUMN)


def get_crop_grouping_faostat_production(model: str, term: dict):
    return get_crop_lookup_value(model, term.get('@id'), term.get('@id'), FAOSTAT_PRODUCTION_LOOKUP_COLUMN)


def get_N2ON_fertiliser_coeff_from_primary_product(model: str, log_id: str, cycle: dict):
    product = find_primary_product(cycle)
    term_id = product.get('term', {}).get('@id') if product else None
    percent = get_crop_lookup_value(model, log_id, term_id, 'N2ON_FERT') if term_id else None
    return safe_parse_float(percent, default=0.01)


def is_plantation(model: str, log_id: str, term_id: str):
    return get_crop_lookup_value(model, log_id, term_id, 'isPlantation')


def is_permanent_crop(model: str, log_id: str, term: dict):
    return get_crop_grouping_fao(model, log_id, term) == 'Permanent crops'


def valid_site_type(cycle: dict, include_permanent_pasture=False):
    """
    Check if the `site.siteType` of the cycle is `cropland`.

    Parameters
    ----------
    cycle : dict
        The `Cycle`.
    include_permanent_pasture : bool
        If set to `True`, `permanent pasture` is also allowed. Defaults to `False`.

    Returns
    -------
    bool
        `True` if `siteType` matches the allowed values, `False` otherwise.
    """
    site_types = [SiteSiteType.CROPLAND.value] + (
        [SiteSiteType.PERMANENT_PASTURE.value] if include_permanent_pasture else []
    )
    return site_valid_site_type(cycle.get('site', {}), site_types)


def get_landCover_term_id(lookup_term: dict, **log_args) -> str:
    value = get_lookup_value(lookup_term, 'landCoverTermId', **log_args)
    return (
        lookup_term.get("@id") if lookup_term.get("termType") == TermTermType.LANDCOVER.value else
        value.split(';')[0] if isinstance(value, str) else
        None
    )
