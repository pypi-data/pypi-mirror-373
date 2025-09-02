from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugMissingLookup, logRequirements
from hestia_earth.models.utils.impact_assessment import get_site, get_country_id
from hestia_earth.models.utils.lookup import get_region_lookup_value
from . import MODEL


def _lookup_value(term_id: str, lookup_name: str, col_match: str, col_val: str, column: str):
    value = get_table_value(download_lookup(lookup_name), col_match, col_val, column_name(column))
    debugMissingLookup(lookup_name, col_match, col_val, column, value, model=MODEL, term=term_id)
    return value


def get_region_factor(
    term_id: str, impact_assessment: dict, lookup_suffix: str, group_key: str = None, blank_node: dict = None
):
    site = get_site(impact_assessment)
    ecoregion = site.get('ecoregion')
    country_id = get_country_id(impact_assessment, blank_node=blank_node)
    site_type = site.get('siteType')

    lookup_prefix = 'ecoregion' if ecoregion else 'region' if country_id else None
    lookup_name = f"{lookup_prefix}-siteType-{lookup_suffix}.csv"

    logRequirements(impact_assessment, model=MODEL, term=term_id,
                    site_type=site_type,
                    ecoregion=ecoregion,
                    country_id=country_id)

    value = get_region_lookup_value(
        lookup_name, country_id, site_type, model=MODEL, term=term_id
    ) if lookup_prefix == 'region' else _lookup_value(
        term_id, lookup_name, 'ecoregion', ecoregion, site_type
    )
    value = extract_grouped_data(value, group_key) if group_key else value
    return safe_parse_float(value, default=None)
