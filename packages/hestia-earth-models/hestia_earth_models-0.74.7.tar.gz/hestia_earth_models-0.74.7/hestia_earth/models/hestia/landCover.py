import functools
import math
from collections import defaultdict
from datetime import datetime, timedelta
from hestia_earth.schema import SiteSiteType, TermTermType
from hestia_earth.utils.lookup import (
    download_lookup, get_table_value, column_name, _is_missing_value, extract_grouped_data, lookup_columns
)
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float, to_precision

from hestia_earth.models.log import logRequirements, log_as_table, logShouldRun
from hestia_earth.models.utils import _omit
from hestia_earth.models.utils.constant import DAYS_IN_YEAR
from hestia_earth.models.utils.management import _new_management
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.lookup import get_region_lookup, get_region_lookup_value
from hestia_earth.models.utils.blank_node import DatestrFormat, _gapfill_datestr, DatestrGapfillMode
from .utils import (
    IPCC_LAND_USE_CATEGORY_ANNUAL,
    IPCC_LAND_USE_CATEGORY_PERENNIAL,
    LAND_USE_TERMS_FOR_TRANSFORMATION,
    ANNUAL_CROPLAND,
    PERMANENT_CROPLAND,
    FOREST_LAND,
    OTHER_LAND,
    PERMANENT_PASTURE,
    TOTAL_CROPLAND,
    TOTAL_AGRICULTURAL_CHANGE,
    ALL_LAND_USE_TERMS,
    crop_ipcc_land_use_category
)
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "siteType": [
            "forest",
            "cropland",
            "permanent pasture",
            "other natural vegetation"
        ],
        "country": {"@type": "Term", "termType": "region"},
        "management": [
            {
                "@type": "Management",
                "value": "",
                "term.termType": "landCover",
                "or": {
                    "startDate": "",
                    "endDate": ""
                }
            }
        ]
    }
}
RETURNS = {
    "Management": [{
        "term.termType": "landCover",
        "value": "",
        "endDate": "",
        "startDate": ""
    }]
}
LOOKUPS = {
    "region-crop-cropGroupingFAOSTAT-landCover-annualCropland": "",
    "region-crop-cropGroupingFAOSTAT-landCover-forest": "",
    "region-crop-cropGroupingFAOSTAT-landCover-otherLand": "",
    "region-crop-cropGroupingFAOSTAT-landCover-permanentCropland": "",
    "region-crop-cropGroupingFAOSTAT-landCover-permanentPasture": "",
    "region-crop-cropGroupingFaostatProduction-areaHarvestedUpTo20YearExpansion": "",
    "region-crop-cropGroupingFaostatProduction-areaHarvested": "",
    "region-faostatArea-UpTo20YearExpansion": "",
    "region-faostatArea": [
        "Arable land",
        "Cropland",
        "Forest land",
        "Land area",
        "Other land",
        "Permanent crops",
        "Permanent meadows and pastures"
    ],
    "crop": ["cropGroupingFaostatArea", "IPCC_LAND_USE_CATEGORY"],
    "landCover": ["cropGroupingFaostatProduction", "FAOSTAT_LAND_AREA_CATEGORY"],
    "property": "CALCULATE_TOTAL_LAND_COVER_SHARE_SEPARATELY"
}
MODEL_KEY = 'landCover'

_LAND_AREA = LOOKUPS["region-faostatArea"][3]
_ALLOWED_SITE_TYPES = {
    SiteSiteType.CROPLAND.value,
    SiteSiteType.FOREST.value,
    SiteSiteType.OTHER_NATURAL_VEGETATION.value,
    SiteSiteType.PERMANENT_PASTURE.value
}
_BUILDING_SITE_TYPES = [
    SiteSiteType.AGRI_FOOD_PROCESSOR.value,
    SiteSiteType.ANIMAL_HOUSING.value,
    SiteSiteType.FOOD_RETAILER.value
]
_DEFAULT_WINDOW_IN_YEARS = 20
_DATE_TOLERANCE_IN_YEARS = 2
_OUTPUT_SIGNIFICANT_DIGITS = 3
_ALLOWED_LAND_USE_TYPES = [ANNUAL_CROPLAND, PERMANENT_CROPLAND, PERMANENT_PASTURE, TOTAL_CROPLAND]
_TOP_LEVEL_LAND_USE_TYPE_IDS = {"annualCropland", "permanentCropland", "permanentPasture", "cropland"}
_LOOKUP_EXPANSION = "region-crop-cropGroupingFaostatProduction-areaHarvestedUpTo20YearExpansion.csv"
_COMPLETE_CHANGES_OTHER_LAND = {
    OTHER_LAND: 1,
    FOREST_LAND: 0,
    PERMANENT_PASTURE: 0,
    ANNUAL_CROPLAND: 0,
    PERMANENT_CROPLAND: 0
}


def _get_lookup_with_cache(lookup_term, column):
    """Wrapper to get_lookup_value which pulls out the immutable parts of the term to allow caching."""
    @functools.cache
    def _get_immutable_lookup(term_id: str, term_type: str, col: str):
        new_term = {"@id": term_id, "termType": term_type} if term_type and term_id else {}
        return get_lookup_value(
            lookup_term=new_term,
            column=col,
            skip_debug=False,
            model=MODEL,
            term=new_term
        )

    return _get_immutable_lookup(
        term_id=lookup_term.get("@id"),
        term_type=lookup_term.get("termType"),
        col=column
    )


def _get_land_cover_lookup_suffix(land_type: str) -> str:
    return LAND_USE_TERMS_FOR_TRANSFORMATION[land_type][0]


def get_landCover_lookups(country_id: str, end_year: int, product_name: str):
    """
    Attempts to get the pre-calculated values for the landCover model calculation.
    Returns: {"Arable land": <value>, "Forest land": <value>, "Other land": <value>,
              "Permanent crops": <value>, "Permanent meadows and pastures": <value>}
    Missing values are returned as None.
    """
    lookup_prefix = 'region-crop-cropGroupingFAOSTAT-landCover'
    return {
        # Divide by 100 to match site_area ratios
        land_type: value / 100 if value is not None else value
        for land_type, value in
        {
            land_type: safe_parse_float(
                value=extract_grouped_data(
                    data=get_region_lookup_value(
                        lookup_name=f"{lookup_prefix}-{_get_land_cover_lookup_suffix(land_type)}.csv",
                        term_id=country_id,
                        column=product_name,
                        model=MODEL,
                        key=MODEL_KEY
                    ),
                    key=str(end_year)
                ),
                default=None
            )
            for land_type in LAND_USE_TERMS_FOR_TRANSFORMATION.keys()
        }.items()
    }


def _management(term_id: str, value: float, start_date: str, end_date: str):
    node = _new_management(term_id, MODEL)
    node['value'] = value
    node['startDate'] = start_date
    node['endDate'] = end_date
    return node


def _is_missing_or_none(value) -> bool:
    return value is None or _is_missing_value(value)


def _safe_divide(numerator, denominator, default=0) -> float:
    return default if not denominator else numerator / denominator


def scale_values_to_one(dictionary: dict) -> dict:
    """
    Takes a dictionary with numeric values.
    Scales each value so that the sum of them all is one.
    """
    # Does not handle negative values.
    sum_of_values = sum(dictionary.values())
    return {key: value / sum_of_values for key, value in dictionary.items()} if sum_of_values != 0 else dictionary


def cap_values(dictionary: dict, lower_limit: float = 0, upper_limit: float = 1) -> dict:
    return {key: min([upper_limit, max([lower_limit, value])]) for key, value in dictionary.items()}


def site_area_sum_to_100(dict_of_percentages: dict):
    return False if dict_of_percentages == {} else (
        math.isclose(sum(dict_of_percentages.values()), 1.0, rel_tol=0.05) or
        math.isclose(sum(dict_of_percentages.values()), 0.0, rel_tol=0.01)
    )


def _should_group_landCover(management_node: dict):
    return any(
        bool(_get_lookup_with_cache(
            lookup_term=prop.get("term", {}),
            column="CALCULATE_TOTAL_LAND_COVER_SHARE_SEPARATELY"
        ))
        for prop in management_node.get("properties", [])
    )


def _get_changes(country_id: str, end_year: int) -> tuple[dict, list]:
    """
    For each entry in ALL_LAND_USE_TERMS, creates a key: value in output dictionary, also TOTAL
    """
    lookup_name = "region-faostatArea-UpTo20YearExpansion.csv"
    changes_dict = {
        land_use_term: safe_parse_float(
            extract_grouped_data(
                get_region_lookup_value(lookup_name, country_id, land_use_term, model=MODEL, key=MODEL_KEY),
                str(end_year)
            ),
            default=None
        )
        for land_use_term in ALL_LAND_USE_TERMS + [_LAND_AREA]
    }
    missing_changes = [k for k, v in changes_dict.items() if v is None]
    changes_dict = {k: v if v is not None else 0 for k, v in changes_dict.items()}
    changes_dict[TOTAL_AGRICULTURAL_CHANGE] = (
        float(changes_dict.get(TOTAL_CROPLAND, 0)) + float(changes_dict.get(PERMANENT_PASTURE, 0))
    )

    return changes_dict, missing_changes


def _get_ratio_start_and_end_values(
    expansion: float,
    fao_name: str,
    country_id: str,
    end_year: int
) -> float:
    # expansion over twenty years / current area
    table_value = get_region_lookup_value('region-faostatArea.csv', country_id, fao_name, model=MODEL, key=MODEL_KEY)
    end_value = safe_parse_float(value=extract_grouped_data(table_value, str(end_year)), default=None)
    return max(0.0, _safe_divide(numerator=expansion, denominator=end_value))


def _get_ratio_between_land_use_types(
    country_id: str,
    end_year: int,
    first_land_use_term: str,
    second_land_use_term: str
) -> tuple:
    """Returns a tuple of the values of the two land use terms for the same country and year."""
    return tuple([
        safe_parse_float(value=extract_grouped_data(
            get_region_lookup_value(
                'region-faostatArea.csv', country_id, land_use_term, model=MODEL, key=MODEL_KEY
            ),
            str(end_year)),
            default=None
        )
        for land_use_term in [first_land_use_term, second_land_use_term]
    ])


def _estimate_maximum_forest_change(
    forest_change: float, total_cropland_change: float, pasture_change: float, total_agricultural_change: float
):
    """
    (L): Estimate maximum forest loss
    Gives a negative number representing forest loss. Does not currently handle forest gain.
    """
    positive_change = pasture_change > 0 and total_cropland_change > 0
    return _negative_agricultural_land_change(
        forest_change=forest_change,
        pasture_change=pasture_change,
        total_cropland_change=total_cropland_change
    ) if not positive_change else (
        -total_agricultural_change
        if -min(forest_change, 0) > total_agricultural_change else
        min(forest_change, 0)
    )


def _negative_agricultural_land_change(forest_change, pasture_change, total_cropland_change):
    return (
        -pasture_change if 0 < pasture_change < -min(forest_change, 0)
        else min(forest_change, 0) if pasture_change > 0
        else -total_cropland_change if 0 < total_cropland_change < -min(forest_change, 0)
        else min(forest_change, 0) if 0 < total_cropland_change
        else 0
    )


def _allocate_forest_loss(forest_loss: float, changes: dict):
    """Allocate forest loss between agricultural categories for the specific country"""
    return {
        TOTAL_CROPLAND: forest_loss * _safe_divide(
            numerator=max(changes[TOTAL_CROPLAND], 0),
            denominator=max(changes[TOTAL_CROPLAND], 0) + max(changes[PERMANENT_PASTURE], 0)
        ),
        PERMANENT_PASTURE: forest_loss * _safe_divide(
            numerator=max(changes[PERMANENT_PASTURE], 0),
            denominator=max(changes[TOTAL_CROPLAND], 0) + max(changes[PERMANENT_PASTURE], 0)
        )
    }


def _additional_allocation(changes, max_forest_loss_to_cropland, max_forest_loss_to_permanent_pasture):
    """Determine how much area still needs to be assigned"""
    return {
        TOTAL_CROPLAND: max(changes[TOTAL_CROPLAND], 0) + max_forest_loss_to_cropland,
        PERMANENT_PASTURE: max(changes[PERMANENT_PASTURE], 0) + max_forest_loss_to_permanent_pasture
    }


def _allocate_cropland_loss_to_pasture(changes: dict, land_required_for_permanent_pasture: float):
    """Allocate changes between Permanent pasture and cropland"""
    return (
        max(-land_required_for_permanent_pasture, changes[TOTAL_CROPLAND])
        if changes[TOTAL_CROPLAND] < 0 else 0
    )


def _allocate_pasture_loss_to_cropland(changes: dict, land_required_for_cropland: float):
    """Allocate changes between Permanent pasture and cropland"""
    return (
        max(-land_required_for_cropland, changes[PERMANENT_PASTURE])
        if changes[PERMANENT_PASTURE] < 0 else 0
    )


def _allocate_other_land(
    changes: dict, max_forest_loss_to: dict, pasture_loss_to_cropland: float, cropland_loss_to_pasture: float
) -> dict:
    """Allocate changes between Other land and cropland"""
    other_land_loss_to_cropland = (
        -(max(changes[TOTAL_CROPLAND], 0) + max_forest_loss_to[TOTAL_CROPLAND]
          + pasture_loss_to_cropland)
    )
    other_land_loss_to_pasture = (
        -(max(changes[PERMANENT_PASTURE], 0) + max_forest_loss_to[PERMANENT_PASTURE]
          + cropland_loss_to_pasture)
    )
    return {
        TOTAL_CROPLAND: other_land_loss_to_cropland,
        PERMANENT_PASTURE: other_land_loss_to_pasture,
        TOTAL_AGRICULTURAL_CHANGE: other_land_loss_to_cropland + other_land_loss_to_pasture
    }


def _allocate_annual_permanent_cropland_losses(changes: dict) -> tuple:
    """
    (Z, AA): Allocate changes between Annual cropland and Permanent cropland
    Returns: annual_cropland_loss_to_permanent_cropland, permanent_cropland_loss_to_annual_cropland
    """
    return (
        -min(-changes[ANNUAL_CROPLAND], changes[PERMANENT_CROPLAND])
        if (changes[ANNUAL_CROPLAND] < 0 and changes[PERMANENT_CROPLAND] > 0) else 0,
        -min(changes[ANNUAL_CROPLAND], -changes[PERMANENT_CROPLAND])
        if (changes[ANNUAL_CROPLAND] > 0 and changes[PERMANENT_CROPLAND] < 0) else 0
    )


def _estimate_conversions_to_annual_cropland(
    changes: dict,
    pasture_loss_to_crops: float,
    forest_loss_to_cropland: float,
    other_land_loss_to_annual_cropland: float,
    permanent_to_annual_cropland: float
) -> dict:
    """(AC-AG): Estimate percentage of land sources when converted to: Annual cropland"""

    # -> percent_annual_cropland_was[]
    def conversion_to_annual_cropland(factor: float):
        return factor * _safe_divide(
            numerator=_safe_divide(
                numerator=max(changes[ANNUAL_CROPLAND], 0),
                denominator=max(changes[ANNUAL_CROPLAND], 0) + max(changes[PERMANENT_CROPLAND], 0)
            ),
            denominator=-changes[ANNUAL_CROPLAND]
        )

    percentages = {
        FOREST_LAND: conversion_to_annual_cropland(forest_loss_to_cropland),
        OTHER_LAND: conversion_to_annual_cropland(other_land_loss_to_annual_cropland),
        PERMANENT_PASTURE: conversion_to_annual_cropland(pasture_loss_to_crops),
        PERMANENT_CROPLAND: _safe_divide(numerator=permanent_to_annual_cropland, denominator=-changes[ANNUAL_CROPLAND])
    }
    return percentages


def _estimate_conversions_to_permanent_cropland(
    changes: dict,
    annual_loss_to_permanent_cropland: float,
    pasture_loss_to_cropland: float,
    forest_loss_to_cropland: float,
    other_land_loss_to_annual_cropland: float
) -> dict:
    """Estimate percentage of land sources when converted to: Permanent cropland"""

    def conversion_to_permanent_cropland(factor: float):
        return _safe_divide(
            numerator=_safe_divide(
                numerator=factor * max(changes[PERMANENT_CROPLAND], 0),
                denominator=max(changes[ANNUAL_CROPLAND], 0) + max(changes[PERMANENT_CROPLAND], 0)
            ),
            denominator=-changes[PERMANENT_CROPLAND]
        )

    percentages = {
        FOREST_LAND: conversion_to_permanent_cropland(forest_loss_to_cropland),
        OTHER_LAND: conversion_to_permanent_cropland(other_land_loss_to_annual_cropland),
        PERMANENT_PASTURE: conversion_to_permanent_cropland(pasture_loss_to_cropland),
        ANNUAL_CROPLAND: conversion_to_permanent_cropland(annual_loss_to_permanent_cropland)
    }
    return percentages


def _estimate_conversions_to_pasture(
    changes: dict,
    forest_loss_to_pasture: float,
    total_cropland_loss_to_pasture: float,
    other_land_loss_to_pasture: float
) -> dict:
    """Estimate percentage of land sources when converted to: Permanent pasture"""
    percentages = {
        FOREST_LAND: _safe_divide(
            numerator=forest_loss_to_pasture,
            denominator=-changes[PERMANENT_PASTURE],
        ),
        OTHER_LAND: _safe_divide(
            numerator=other_land_loss_to_pasture,
            denominator=-changes[PERMANENT_PASTURE]
        ),
        # AT
        ANNUAL_CROPLAND: _safe_divide(
            numerator=total_cropland_loss_to_pasture * _safe_divide(
                numerator=min(changes[ANNUAL_CROPLAND], 0),
                denominator=(min(changes[ANNUAL_CROPLAND], 0) + min(changes[PERMANENT_CROPLAND], 0))
            ),
            denominator=-changes[PERMANENT_PASTURE]
        ),
        PERMANENT_CROPLAND: _safe_divide(
            numerator=total_cropland_loss_to_pasture * _safe_divide(
                numerator=min(changes[PERMANENT_CROPLAND], 0),
                denominator=(min(changes[ANNUAL_CROPLAND], 0) + min(changes[PERMANENT_CROPLAND], 0))
            ),
            denominator=-changes[PERMANENT_PASTURE]
        )
    }
    return percentages


def _get_shares_of_expansion(
    land_use_type: str,
    percent_annual_cropland_was: dict,
    percent_permanent_cropland_was: dict,
    percent_pasture_was: dict
) -> dict:
    expansion_for_type = {
        ANNUAL_CROPLAND: percent_annual_cropland_was,
        PERMANENT_CROPLAND: percent_permanent_cropland_was,
        PERMANENT_PASTURE: percent_pasture_was
    }
    return scale_values_to_one({
        k: expansion_for_type[land_use_type].get(k, 0)
        for k in LAND_USE_TERMS_FOR_TRANSFORMATION.keys()
    })


def _get_faostat_name(term: dict) -> str:
    """For landCover terms, find the cropGroupingFaostatArea name for the landCover id."""
    return _get_lookup_with_cache(term, "cropGroupingFaostatArea")


def _get_most_common_or_alphabetically_first(crop_terms: list) -> str:
    histogram = {term: crop_terms.count(term) for term in crop_terms}
    max_freq = max(histogram.values())
    # Sorted; to be deterministic
    return sorted([term for term, freq in histogram.items() if freq == max_freq])[0]


def _get_complete_faostat_to_crop_mapping() -> dict:
    """Returns mapping in the format: {faostat_name: IPCC_LAND_USE_CATEGORY, ...}"""
    lookup = download_lookup("crop.csv")
    mappings = defaultdict(list)
    for crop_term_id in [row[0] for row in lookup]:
        key = column_name(
            get_table_value(lookup, 'termid', crop_term_id, column_name("cropGroupingFaostatArea"))
        )
        if key:
            mappings[key].append(crop_ipcc_land_use_category(crop_term_id=crop_term_id, lookup_term_type="crop"))
    return {
        fao_name: _get_most_common_or_alphabetically_first(crop_terms)
        for fao_name, crop_terms in mappings.items()
    }


def _get_harvested_area(country_id: str, year: int, faostat_name: str) -> float:
    """
    Returns a dictionary of harvested areas for the country & year, indexed by landCover term (crop)
    """
    lookup_name = "region-crop-cropGroupingFaostatProduction-areaHarvested.csv"

    return safe_parse_float(
        value=extract_grouped_data(
            data=get_region_lookup_value(lookup_name, country_id, faostat_name, model=MODEL, key=MODEL_KEY),
            key=str(year)
        ),
        default=None
    )


def _get_term_id_for_crop(nodes: set, land_type: str) -> str:
    """Use the original crop term id for permanent/perennial crops and the land use id for other types."""
    result = next(
        (node for node in nodes if crop_ipcc_land_use_category(node[0]) == IPCC_LAND_USE_CATEGORY_PERENNIAL), None
    )
    return (
        # Take first perennial crop - not multi-cropping
        result[0] if land_type == PERMANENT_CROPLAND and result else
        LAND_USE_TERMS_FOR_TRANSFORMATION[land_type][0]
    )


def _run(site: dict, existing_nodes: list, percentage_transformed_from: dict):
    start_year = _get_year_from_landCover(existing_nodes[0]) - _DEFAULT_WINDOW_IN_YEARS

    """Creates a list of new management nodes, excluding any dates matching existing ones."""
    existing_nodes_set = {
        (node.get("term", {}).get("@id", ""), node.get("startDate"), node.get("endDate"))
        for node in existing_nodes
    }
    values = [
        {
            "land_management_key": (
                LAND_USE_TERMS_FOR_TRANSFORMATION[land_type], f"{start_year}-01-01", f"{start_year}-12-31"
            ),
            "land_type": land_type,
            "percentage": 0 if ratio == -0.0 else to_precision(
                number=ratio * 100,
                digits=_OUTPUT_SIGNIFICANT_DIGITS
            ),
            "term_id": _get_term_id_for_crop(existing_nodes_set, land_type=land_type)
        }
        for land_type, ratio in percentage_transformed_from.items()
    ]
    values = [v for v in values if v.get("land_management_key") not in existing_nodes_set]

    for value in values:
        logShouldRun(site, MODEL, value.get("term_id"), True, model_key=MODEL_KEY)

    return [
        _management(
            term_id=value.get("term_id"),
            value=value.get("percentage"),
            start_date=value.get("land_management_key")[1],
            end_date=value.get("land_management_key")[2]
        )
        for value in values
    ]


def get_ratio_of_expanded_area(country_id: str, fao_name: str, end_year: int) -> float:
    table_value = get_region_lookup_value(_LOOKUP_EXPANSION, country_id, fao_name, model=MODEL, key=MODEL_KEY)
    expansion = safe_parse_float(value=extract_grouped_data(table_value, str(end_year)), default=None)
    end_value = _get_harvested_area(
        country_id=country_id,
        year=end_year,
        faostat_name=fao_name
    )
    return 0.0 if any([expansion is None, end_value is None]) else max(
        0.0, _safe_divide(numerator=expansion, denominator=end_value)
    )


def _get_sum_for_land_category(
    values: dict,
    year: int,
    ipcc_land_use_category,
    fao_stat_to_ipcc_type: dict,
    include_negatives: bool = True
) -> float:
    return sum([
        safe_parse_float(value=extract_grouped_data(table_value, str(year)), default=None)
        for fao_name, table_value in values.items()
        if not _is_missing_or_none(extract_grouped_data(table_value, str(year))) and
        fao_stat_to_ipcc_type[fao_name] == ipcc_land_use_category and
        (
            include_negatives or
            safe_parse_float(value=extract_grouped_data(table_value, str(year)), default=None) > 0.0
        )
    ])


def _get_sums_of_crop_expansion(country_id: str, year: int, include_negatives: bool = True) -> tuple[float, float]:
    """
    Sum net expansion for all annual and permanent crops, returned as two values.
    Returns a tuple of (expansion of annual crops, expansion of permanent crops)
    """
    lookup = get_region_lookup(lookup_name=_LOOKUP_EXPANSION, term_id=country_id)
    columns = lookup_columns(lookup)
    values = {
        name: get_table_value(lookup, 'termid', country_id, column_name(name))
        for name in columns if name != "termid"
    }

    fao_stat_to_ipcc_type = _get_complete_faostat_to_crop_mapping()

    annual_sum_of_expansion = _get_sum_for_land_category(
        values=values,
        year=year,
        ipcc_land_use_category=IPCC_LAND_USE_CATEGORY_ANNUAL,
        fao_stat_to_ipcc_type=fao_stat_to_ipcc_type,
        include_negatives=include_negatives
    )
    permanent_sum_of_expansion = _get_sum_for_land_category(
        values=values,
        year=year,
        ipcc_land_use_category=IPCC_LAND_USE_CATEGORY_PERENNIAL,
        fao_stat_to_ipcc_type=fao_stat_to_ipcc_type,
        include_negatives=include_negatives
    )

    return annual_sum_of_expansion, permanent_sum_of_expansion


def _get_net_expansion_cultivated_vs_harvested(
    annual_crops_net_expansion, changes, land_use_type, permanent_crops_net_expansion
):
    return (
        _safe_divide(
            numerator=max(0, changes[ANNUAL_CROPLAND]),
            denominator=(annual_crops_net_expansion / 1000)
        ) if land_use_type == ANNUAL_CROPLAND else
        _safe_divide(
            numerator=max(0, changes[PERMANENT_CROPLAND]),
            denominator=(permanent_crops_net_expansion / 1000)
        ) if land_use_type == PERMANENT_CROPLAND else
        1
    )


def _get_year_from_landCover(node: dict):
    date = node.get('startDate') or node.get('endDate')
    return int(date[:4])


def _scale_site_area_errors(site_area: dict) -> dict:
    """Redistribute the result of any rounding error in proportion to the other land use types."""
    # Positive errors would not have been capped, so won't be missing.
    negative_errors = [v for v in site_area.values() if v < 0.0]
    return {k: v + negative_errors[0] * v for k, v in site_area.items()} \
        if negative_errors and abs(negative_errors[0]) < 1 and all([v < 1 for v in site_area.values()]) else site_area


def _new_landCover_term(new_land_use_term) -> dict:
    return {
        "@id": LAND_USE_TERMS_FOR_TRANSFORMATION[new_land_use_term][0],
        "name": LAND_USE_TERMS_FOR_TRANSFORMATION[new_land_use_term][1],
        "@type": "Term",
        "termType": TermTermType.LANDCOVER.value
    }


def _scaled_value(
    permanent_crops_value: float,
    annual_crops_value: float,
    permanent_crops_factor: float,
    annual_crops_factor: float,
):
    total_area = permanent_crops_factor + annual_crops_factor
    permanent_crops_scaled = permanent_crops_value * permanent_crops_factor / total_area
    annual_crops_scaled = annual_crops_value * annual_crops_factor / total_area
    return annual_crops_scaled + permanent_crops_scaled


def _scale_from_annual_and_permanent_results(
    annual_cropland_results: dict,
    permanent_cropland_results: dict,
    annual_cropland_factor: float,
    permanent_cropland_factor: float
) -> dict:
    return {
        land_key: _scaled_value(
            permanent_crops_value=permanent_cropland_results[land_key],
            annual_crops_value=land_value,
            permanent_crops_factor=permanent_cropland_factor,
            annual_crops_factor=annual_cropland_factor
        )
        for land_key, land_value in annual_cropland_results.items()
    }


def _should_run_historical_land_use_change(site: dict, nodes: list, land_use_type: str) -> tuple[bool, dict]:
    # Assume a single management node for single-cropping.
    return (
        _should_run_historical_land_use_change_total_cropland(site, nodes) if land_use_type == TOTAL_CROPLAND else
        _should_run_historical_land_use_change_single_crop(
            site=site,
            term=nodes[0].get("term", {}),
            country_id=site.get("country", {}).get("@id"),
            end_year=_get_year_from_landCover(nodes[0]),
            land_use_type=land_use_type
        )
    )


def _should_run_historical_land_use_change_total_cropland(site: dict, nodes: list) -> tuple[bool, dict]:
    end_year = _get_year_from_landCover(nodes[0])
    country_id = site.get("country", {}).get("@id")

    # Run _should_run_historical_land_use_change_single_crop for annual and permanent
    should_run_annual, areas_for_annual_cropland = _should_run_historical_land_use_change_single_crop(
        site=site,
        term=_new_landCover_term(ANNUAL_CROPLAND),
        country_id=country_id,
        end_year=end_year,
        land_use_type=ANNUAL_CROPLAND
    )
    should_run_permanent, areas_for_permanent_cropland = _should_run_historical_land_use_change_single_crop(
        site=site,
        term=_new_landCover_term(PERMANENT_CROPLAND),
        country_id=country_id,
        end_year=end_year,
        land_use_type=PERMANENT_CROPLAND
    )
    # Get current ratios ("Arable land" vs "Permanent crops")
    annual_cropland_factor, permanent_crops_factor = _get_ratio_between_land_use_types(
        country_id=country_id,
        end_year=end_year,
        first_land_use_term=ANNUAL_CROPLAND,
        second_land_use_term=PERMANENT_CROPLAND
    ) if should_run_annual and should_run_permanent else tuple([0, 0])
    scaled_results = _scale_from_annual_and_permanent_results(
        annual_cropland_results=areas_for_annual_cropland,
        permanent_cropland_results=areas_for_permanent_cropland,
        annual_cropland_factor=annual_cropland_factor,
        permanent_cropland_factor=permanent_crops_factor
    ) if should_run_annual and should_run_permanent else {}
    # Scale results according to current ratios.
    return all([should_run_annual, should_run_permanent]), scaled_results


def _log_all_terms(site: dict, land_use_type: str, country_id: str, changes: dict, missing_changes: list):
    for land_use_term, _ in LAND_USE_TERMS_FOR_TRANSFORMATION.values():
        logRequirements(
            log_node=site,
            model=MODEL,
            term=land_use_term,
            model_key=MODEL_KEY,
            land_use_type=land_use_type,
            country_id=country_id,
            changes=log_as_table(changes),
            missing_changes=log_as_table(missing_changes)
        )

        logShouldRun(site, MODEL, land_use_term, False, model_key=MODEL_KEY)


def _should_run_historical_land_use_change_single_crop(
    site: dict,
    term: dict,
    country_id: str,
    end_year: int,
    land_use_type: str
) -> tuple[bool, dict]:
    """Calculate land use change percentages for a single management node/crop."""
    # (C-H).
    changes, missing_changes = _get_changes(country_id=country_id, end_year=end_year)

    # (L). Estimate maximum forest loss
    forest_loss = _estimate_maximum_forest_change(
        forest_change=changes[FOREST_LAND],
        total_cropland_change=changes[TOTAL_CROPLAND],
        pasture_change=changes[PERMANENT_PASTURE],
        total_agricultural_change=changes[TOTAL_AGRICULTURAL_CHANGE]
    )

    # (M, N). Allocate forest loss between agricultural categories for the specific country
    forest_loss_to = _allocate_forest_loss(forest_loss=forest_loss, changes=changes)

    # (P, Q): Determine how much area still needs to be assigned
    land_required_for = _additional_allocation(
        changes=changes,
        max_forest_loss_to_cropland=forest_loss_to[TOTAL_CROPLAND],
        max_forest_loss_to_permanent_pasture=forest_loss_to[PERMANENT_PASTURE]
    )

    # (R): Allocate changes between Permanent pasture and cropland
    cropland_loss_to_pasture = _allocate_cropland_loss_to_pasture(
        changes=changes,
        land_required_for_permanent_pasture=land_required_for[PERMANENT_PASTURE]
    )
    # (S)
    pasture_loss_to_cropland = _allocate_pasture_loss_to_cropland(
        changes=changes,
        land_required_for_cropland=land_required_for[TOTAL_CROPLAND]
    )

    # (V): Allocate changes between Other land and cropland
    other_land_loss_to = _allocate_other_land(
        changes=changes,
        max_forest_loss_to=forest_loss_to,
        pasture_loss_to_cropland=pasture_loss_to_cropland,
        cropland_loss_to_pasture=cropland_loss_to_pasture
    )

    # (Z, AA): Allocate changes between Annual cropland and Permanent cropland
    annual_cropland_loss_to_permanent_cropland, permanent_cropland_loss_to_annual_cropland = (
        _allocate_annual_permanent_cropland_losses(changes)
    )

    # (AC-AG): Estimate percentage of land sources when converted to: Annual cropland
    # Note: All percentages are expressed as decimal fractions. 50% = 0.5
    percent_annual_cropland_was = _estimate_conversions_to_annual_cropland(
        changes=changes,
        pasture_loss_to_crops=pasture_loss_to_cropland,
        forest_loss_to_cropland=forest_loss_to[TOTAL_CROPLAND],
        other_land_loss_to_annual_cropland=other_land_loss_to[TOTAL_CROPLAND],
        permanent_to_annual_cropland=permanent_cropland_loss_to_annual_cropland,
    )

    # (AJ-AM): Estimate percentage of land sources when converted to: Permanent cropland
    percent_permanent_cropland_was = _estimate_conversions_to_permanent_cropland(
        changes=changes,
        annual_loss_to_permanent_cropland=annual_cropland_loss_to_permanent_cropland,
        pasture_loss_to_cropland=pasture_loss_to_cropland,
        forest_loss_to_cropland=forest_loss_to[TOTAL_CROPLAND],
        other_land_loss_to_annual_cropland=other_land_loss_to[TOTAL_CROPLAND]
    )

    # Estimate percentage of land sources when converted to: Permanent pasture
    percent_pasture_was = _estimate_conversions_to_pasture(
        changes=changes,
        forest_loss_to_pasture=forest_loss_to[PERMANENT_PASTURE],
        total_cropland_loss_to_pasture=cropland_loss_to_pasture,
        other_land_loss_to_pasture=other_land_loss_to[PERMANENT_PASTURE]
    )

    # C14-G14
    shares_of_expansion = _get_shares_of_expansion(
        land_use_type=land_use_type,
        percent_annual_cropland_was=percent_annual_cropland_was,
        percent_permanent_cropland_was=percent_permanent_cropland_was,
        percent_pasture_was=percent_pasture_was
    )

    fao_name = _get_faostat_name(term)

    # Cell E8
    expansion_factor = _get_ratio_start_and_end_values(
        expansion=changes[land_use_type],
        fao_name=land_use_type,
        country_id=country_id,
        end_year=end_year
    ) if term.get("@id") in _TOP_LEVEL_LAND_USE_TYPE_IDS or fao_name == "" else get_ratio_of_expanded_area(
        country_id=country_id,
        fao_name=fao_name,
        end_year=end_year
    )

    # E9
    annual_crops_net_expansion, permanent_crops_net_expansion = _get_sums_of_crop_expansion(
        country_id=country_id,
        year=end_year,
        include_negatives=True
    )
    annual_crops_gross_expansion, permanent_crops_gross_expansion = _get_sums_of_crop_expansion(
        country_id=country_id,
        year=end_year,
        include_negatives=False
    )
    e9_net_expansion = _safe_divide(
        numerator=permanent_crops_net_expansion,
        denominator=permanent_crops_gross_expansion
    ) if land_use_type == PERMANENT_CROPLAND else (
        _safe_divide(
            numerator=annual_crops_net_expansion,
            denominator=annual_crops_gross_expansion
        ) if land_use_type == ANNUAL_CROPLAND else 1
    )

    # E10: Compare changes to annual/permanent cropland from net expansion.
    net_expansion_cultivated_vs_harvested = _get_net_expansion_cultivated_vs_harvested(
        annual_crops_net_expansion=annual_crops_net_expansion,
        changes=changes,
        land_use_type=land_use_type,
        permanent_crops_net_expansion=permanent_crops_net_expansion
    )

    site_area = {
        land_type: (
           shares_of_expansion[land_type] * expansion_factor * e9_net_expansion * net_expansion_cultivated_vs_harvested
        ) for land_type in LAND_USE_TERMS_FOR_TRANSFORMATION.keys()
        if land_type != land_use_type
    }
    site_area[land_use_type] = 1 - sum(site_area.values())
    capped_site_area = cap_values(dictionary=_scale_site_area_errors(site_area))

    sum_of_site_areas_is_100 = site_area_sum_to_100(capped_site_area)
    site_type_allowed = site.get("siteType") in _ALLOWED_SITE_TYPES

    logRequirements(
        log_node=site,
        model=MODEL,
        term=term.get("@id"),
        model_key=MODEL_KEY,
        land_use_type=land_use_type,
        country_id=country_id,
        changes=log_as_table(changes),
        missing_changes=log_as_table(missing_changes),
        site_area=log_as_table(capped_site_area),
        sum_of_site_areas_is_100=sum_of_site_areas_is_100,
        site_type_allowed=site_type_allowed
    )

    should_run = all([len(missing_changes) == 0, country_id, site_type_allowed, sum_of_site_areas_is_100])
    logShouldRun(site, MODEL, term.get("@id"), should_run, model_key=MODEL_KEY)
    if not should_run:
        _log_all_terms(
            site=site,
            land_use_type=land_use_type,
            country_id=country_id,
            changes=changes,
            missing_changes=missing_changes
        )

    return should_run, capped_site_area


def _get_land_use_term_from_node(node: dict):
    return _get_lookup_with_cache(lookup_term=node.get("term", {}), column=LOOKUPS.get("landCover")[1])


def _collect_land_use_types(nodes: list) -> list:
    """Look up the land use type from management nodes."""
    return [
        {
            "value": node.get("value", ""),
            "term": node.get("term", {}),
            "id": node.get("term", {}).get("@id"),
            "land-use-type": _get_land_use_term_from_node(node),
            "endDate": _gapfill_datestr(datestr=node.get("endDate"), mode=DatestrGapfillMode.END)[:10],
            "startDate": _gapfill_datestr(datestr=node.get("startDate"), mode=DatestrGapfillMode.START)[:10]
        } for node in nodes
    ]


def _no_prior_land_cover_data(nodes: list, target_node: dict) -> bool:
    """
    Returns true if there are no nodes whose start & end dates the target_node falls within,
    including a tolerance.
    """
    target_date = (
        datetime.strptime(target_node.get('startDate') or target_node.get('endDate'),
                          DatestrFormat.YEAR_MONTH_DAY.value)
        - timedelta(days=_DEFAULT_WINDOW_IN_YEARS * DAYS_IN_YEAR)
    )
    tolerance = timedelta(days=_DATE_TOLERANCE_IN_YEARS * DAYS_IN_YEAR)
    previous_nodes = [
        node for node in nodes
        if datetime.strptime(node.get("startDate"), DatestrFormat.YEAR_MONTH_DAY.value) - tolerance
        < target_date <
        datetime.strptime(node.get("endDate"), DatestrFormat.YEAR_MONTH_DAY.value) + tolerance
    ]
    return len(previous_nodes) == 0


def _should_run(site: dict) -> tuple[bool, list, dict]:
    is_site_building = site.get('siteType') in _BUILDING_SITE_TYPES

    allowed_land_use_types = _ALLOWED_LAND_USE_TYPES + ([OTHER_LAND] if is_site_building else [])

    management_nodes = _collect_land_use_types([
        node for node in filter_list_term_type(site.get("management", []), TermTermType.LANDCOVER)
        if not _should_group_landCover(node)
    ])
    relevant_nodes = sorted(
        [
            node for node in management_nodes
            if node["land-use-type"] in allowed_land_use_types
        ],
        key=lambda n: n.get("startDate") or n.get("endDate")
    )

    land_use_type = relevant_nodes[0].get("land-use-type") if relevant_nodes else None

    has_no_prior_land_cover_data = _no_prior_land_cover_data(
        nodes=management_nodes,
        target_node=relevant_nodes[0]
    ) if relevant_nodes else None

    landCover_from_lookups = get_landCover_lookups(
        country_id=site.get("country", {}).get("@id"),
        end_year=_get_year_from_landCover(relevant_nodes[0]),
        product_name=relevant_nodes[0].get("term", {}).get("name", "")
    ) if relevant_nodes else {}

    should_run_nodes, site_area = (
        (False, {}) if not all([land_use_type, has_no_prior_land_cover_data])
        else (True, landCover_from_lookups) if landCover_from_lookups and all(landCover_from_lookups.values())
        else (True, _COMPLETE_CHANGES_OTHER_LAND) if is_site_building
        else _should_run_historical_land_use_change(
            site=site,
            nodes=relevant_nodes,
            land_use_type=land_use_type
        )
    )

    logRequirements(site, model=MODEL, model_key=MODEL_KEY,
                    has_management_nodes=bool(relevant_nodes),
                    land_use_type=land_use_type,
                    allowed_land_use_types=';'.join(allowed_land_use_types),
                    has_no_prior_land_cover_data=has_no_prior_land_cover_data,
                    management_nodes=log_as_table([_omit(n, ['term']) for n in relevant_nodes]),
                    landCover_from_lookups=log_as_table([
                        {land_type: value} for land_type, value in landCover_from_lookups.items()
                    ]),
                    should_run_nodes=should_run_nodes)

    should_run = all([land_use_type, has_no_prior_land_cover_data, should_run_nodes])
    logShouldRun(site, MODEL, None, should_run, model_key=MODEL_KEY)
    return should_run_nodes, relevant_nodes, site_area


def run(site: dict) -> list:
    should_run, relevant_nodes, site_area = _should_run(site=site)
    return _run(site, relevant_nodes, site_area) if should_run else []
