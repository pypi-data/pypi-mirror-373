from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.lookup import download_lookup, _get_single_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logRequirements, debugMissingLookup, logShouldRun
from hestia_earth.models.utils import sum_values, multiply_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import (
    convert_value_from_cycle, get_product, get_site, get_region_id
)
from hestia_earth.models.utils.input import sum_input_impacts
from hestia_earth.models.utils.lookup import get_region_lookup_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "or": {
                "awareWaterBasinId": "",
                "country": {"@type": "Term", "termType": "region"}
            }
        },
        "optional": {
            "emissionsResourceUse": [{
                "@type": "Indicator",
                "term.@id": "freshwaterWithdrawalsDuringCycle",
                "value": ""
            }]
        }
    }
}
RETURNS = {
    "Indicator": [{
        "value": ""
    }]
}
LOOKUPS = {
    "@doc": "Different lookup files are used depending on the situation",
    "awareWaterBasinId-2-0": ["CFs_agri", "CFs_nonagri", "CFs_unspecified"],
    "region-aware-2-0-factors": ["CFs_agri", "CFs_nonagri", "CFs_unspecified"]
}
TERM_ID = 'scarcityWeightedWaterUse'
AWARE_KEY = 'awareWaterBasinId'
AGRI_SITE_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value,
    SiteSiteType.PERMANENT_PASTURE.value
]
_REGION_LOOKUP = 'region-aware-2-0-factors.csv'
_AWARE_LOOKUP = 'awareWaterBasinId-2-0.csv'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    return indicator


def _lookup_column(site: dict):
    site_type = site.get('siteType')
    return (
        'CFs_unspecified' if not site_type else
        'CFs_agri' if site_type in AGRI_SITE_TYPES else
        'CFs_nonagri'
    )


def _get_factor_from_basinId(site: dict, aware_id: str):
    lookup_col = _lookup_column(site)
    lookup = download_lookup(_AWARE_LOOKUP)
    try:
        value = _get_single_table_value(lookup, column_name(AWARE_KEY), int(aware_id), column_name(lookup_col))
    except Exception:
        value = None
    debugMissingLookup(_AWARE_LOOKUP, AWARE_KEY, aware_id, lookup_col, value, model=MODEL, term=TERM_ID)
    return safe_parse_float(value, default=None)


def _get_factor_from_region(impact_assessment: dict, fresh_water: dict, site: dict):
    region_id = get_region_id(impact_assessment, fresh_water)
    lookup_col = _lookup_column(site)
    value = get_region_lookup_value(_REGION_LOOKUP, region_id, lookup_col, model=MODEL, term=TERM_ID)
    return safe_parse_float(value, default=None)


def run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    fresh_water = find_term_match(impact_assessment.get('emissionsResourceUse', []), 'freshwaterWithdrawalsDuringCycle')
    site = get_site(impact_assessment)
    aware_id = site.get(AWARE_KEY)
    factor = (
        _get_factor_from_basinId(site, aware_id) if aware_id else None
    ) or _get_factor_from_region(impact_assessment, fresh_water, site)
    inputs_value = convert_value_from_cycle(
        impact_assessment, product, sum_input_impacts(cycle.get('inputs', []), TERM_ID), model=MODEL, term_id=TERM_ID
    )

    value = sum_values([
        multiply_values([fresh_water.get('value'), factor]),
        inputs_value
    ])

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    fresh_water=fresh_water.get('value'),
                    aware_id=aware_id,
                    factor=factor,
                    inputs_value=inputs_value)

    should_run = all([value is not None])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)

    return [_indicator(value)] if should_run else []
