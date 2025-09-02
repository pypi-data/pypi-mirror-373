from enum import Enum
from typing import Literal
import numpy as np

from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.model import find_primary_product

from hestia_earth.models.log import debugMissingLookup
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.ecoClimateZone import EcoClimateZone, get_ecoClimateZone_lookup_grouped_value
from hestia_earth.models.utils.term import get_lookup_value

from . import MODEL

_PRODUCT_LOOKUP = "IPCC_2013_ORGANIC_SOIL_CULTIVATION_CATEGORY"
_DITCH_LOOKUP = "IPCC_2013_DRAINED_ORGANIC_SOILS_DITCH_FRAC_"
_FACTOR_LOOKUPS = {
    "ch4ToAirOrganicSoilCultivation": "IPCC_2013_ORGANIC_SOILS_KG_CH4_HECTARE_",
    "co2ToAirOrganicSoilCultivation": "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_",
    "n2OToAirOrganicSoilCultivationDirect": "IPCC_2013_ORGANIC_SOILS_KG_N2O-N_HECTARE_"
}
_NETHERLANDS_TERM_ID = "GADM-NLD"

_CONVERSION_FACTORS = {
    "co2ToAirOrganicSoilCultivation": 1000 * get_atomic_conversion(Units.KG_CO2, Units.TO_C),
    "n2OToAirOrganicSoilCultivationDirect": get_atomic_conversion(Units.KG_N2O, Units.TO_N)
}
_DEFAULT_FACTOR = {"value": 0}
_EXCLUDED_ECO_CLIMATE_ZONES = [EcoClimateZone.POLAR_MOIST, EcoClimateZone.POLAR_DRY]


class OrganicSoilCategory(Enum):
    ANNUAL_CROPS = "Annual crops"
    PERENNIAL_CROPS = "Perennial crops"
    ACACIA = "Acacia"
    OIL_PALM = "Oil palm"
    SAGO_PALM = "Sago palm"
    PADDY_RICE_CULTIVATION = "Paddy rice cultivation"
    GRASSLAND = "Grassland"
    DITCH = "Ditch"
    OTHER = "Other"


class DitchCategory(Enum):
    AGRICULTURAL_LAND = "Agricultural land"
    NETHERLANDS = "Netherlands"


def assign_organic_soil_category(cycle: dict, log_id: str) -> OrganicSoilCategory:
    """
    Assign an emission factor category to a cycle based on `site.siteType` and primary product.

    Cropland cycles without a primary product cannot be categorised - the function will return
    `OrganicSoilCategory.OTHER`.
    """
    site = cycle.get("site", {})
    site_type = site.get("siteType", None)

    if site_type == SiteSiteType.PERMANENT_PASTURE.value:
        return OrganicSoilCategory.GRASSLAND

    product = find_primary_product(cycle)

    if product is None:
        return OrganicSoilCategory.OTHER

    lookup_value = get_lookup_value(product.get("term", {}), _PRODUCT_LOOKUP, model=MODEL, term=log_id)

    return (
        next(
            (category for category in OrganicSoilCategory if lookup_value == category.value),
            OrganicSoilCategory.OTHER
        )
        if lookup_value else OrganicSoilCategory.OTHER
    )


def assign_ditch_category(cycle: dict) -> DitchCategory:
    """
    Assign a ditch category to a cycle based. Cycles that take place in Netherlands are given a special category, all
    others return the default.
    """
    site = cycle.get("site", {})
    country_id = site.get("country", {}).get("@id")
    return DitchCategory.NETHERLANDS if country_id == _NETHERLANDS_TERM_ID else DitchCategory.AGRICULTURAL_LAND


def get_emission_factor(
    emission_id: Literal[
        "co2ToAirOrganicSoilCultivation",
        "ch4ToAirOrganicSoilCultivation",
        "n2OToAirOrganicSoilCultivationDirect"
    ],
    eco_climate_zone: EcoClimateZone,
    organic_soil_category: OrganicSoilCategory
) -> dict:
    """
    Retrieve emission factor data from the eco-climate zone lookup.
    """
    col_name = "".join([_FACTOR_LOOKUPS[emission_id], organic_soil_category.name])
    row_value = eco_climate_zone.value

    data = get_ecoClimateZone_lookup_grouped_value(row_value, col_name)
    debugMissingLookup("ecoClimateZone.csv", "ecoClimateZone", row_value, col_name, data, model=MODEL, term=emission_id)

    return data or _DEFAULT_FACTOR


def get_ditch_frac(
    eco_climate_zone: EcoClimateZone,
    ditch_category: DitchCategory,
    **debug_kwargs: dict
) -> dict:
    """
    Retrieve ditch fraction data from the eco-climate zone lookup.
    """
    col_name = "".join([_DITCH_LOOKUP, ditch_category.name])
    row_value = eco_climate_zone.value

    data = get_ecoClimateZone_lookup_grouped_value(row_value, col_name)
    debugMissingLookup("ecoClimateZone.csv", "ecoClimateZone", row_value, col_name, data, model=MODEL, **debug_kwargs)

    return data or _DEFAULT_FACTOR


def calc_emission(
    emission_id: Literal[
        "co2ToAirOrganicSoilCultivation",
        "ch4ToAirOrganicSoilCultivation",
        "n2OToAirOrganicSoilCultivationDirect"
    ],
    emission_factor: float,
    histosol: float,
    land_occupation: float
):
    """
    Calculate the emission and convert it to kg/ha-1.
    """
    return emission_factor * land_occupation * histosol * _CONVERSION_FACTORS.get(emission_id, 1) / 100


def remap_categories(
    category: OrganicSoilCategory,
    mapping: dict[OrganicSoilCategory, OrganicSoilCategory]
) -> OrganicSoilCategory:
    """
    Remap emission factor categories for cases in which emission factors are not available for a specific category and
    a more general one must be used.
    """
    return mapping.get(category, category)


def valid_eco_climate_zone(
    eco_climate_zone: EcoClimateZone,
):
    """
    Validate that the model should run for a specific eco-climate zone.
    """
    return isinstance(eco_climate_zone, EcoClimateZone) and eco_climate_zone not in _EXCLUDED_ECO_CLIMATE_ZONES


def format_number(value) -> str:
    return f"{value:.3g}" if isinstance(value, (float, int)) else "None"


def format_nd_array(value) -> str:
    return f"{np.mean(value):.3g} ± {np.std(value):.3g}" if isinstance(value, np.ndarray) else "None"
