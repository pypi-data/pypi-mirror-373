from enum import Enum
from functools import reduce
from numpy import empty_like, random, vstack
from numpy.typing import NDArray
from pydash.objects import merge
from typing import Callable, Literal, Optional, Union
from hestia_earth.schema import MeasurementMethodClassification, SiteSiteType, TermTermType
from hestia_earth.utils.blank_node import get_node_value
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.stats import gen_seed
from hestia_earth.utils.descriptive_stats import calc_descriptive_stats

from hestia_earth.models.utils import split_on_condition
from hestia_earth.models.utils.blank_node import (
    cumulative_nodes_match, cumulative_nodes_lookup_match, cumulative_nodes_term_match, group_by_term,
    node_lookup_match, node_term_match, group_nodes_by_year, validate_start_date_end_date
)
from hestia_earth.models.utils.ecoClimateZone import EcoClimateZone, get_eco_climate_zone_value
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.term import get_residue_removed_or_burnt_terms, get_upland_rice_land_cover_terms

from .organicCarbonPerHa_utils import (
    check_irrigation, DEPTH_LOWER, DEPTH_UPPER, IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_LOOKUP_VALUE,
    IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE, IPCC_MANAGEMENT_CATEGORY_TO_GRASSLAND_MANAGEMENT_TERM_ID,
    IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE, IpccSoilCategory, IpccCarbonInputCategory,
    IpccLandUseCategory, IpccManagementCategory, is_cover_crop, MIN_AREA_THRESHOLD, sample_constant,
    sample_plus_minus_error, sample_plus_minus_uncertainty, SITE_TYPE_TO_IPCC_LAND_USE_CATEGORY,
    SUPER_MAJORITY_AREA_THRESHOLD, STATS_DEFINITION
)
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "management": [
            {"@type": "Management", "value": "", "term.termType": "landCover"}
        ],
        "measurements": [
            {
                "@type": "Measurement",
                "value": ["1", "2", "3", "4", "7", "8", "9", "10", "11", "12"],
                "term.@id": "ecoClimateZone"
            }
        ],
        "optional": {
            "measurements": [
                {"@type": "Measurement", "value": "", "term.termType": ["soilType", "usdaSoilType"]}
            ],
            "management": [
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "cropResidueManagement",
                    "name": ["burnt", "removed"]
                },
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "landUseManagement"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.termType": "tillage"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "waterRegime",
                    "name": ["deep water", "irrigated"]
                },
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "amendmentIncreasingSoilCarbonUsed"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.@id": "animalManureUsed"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "inorganicNitrogenFertiliserUsed"
                },
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "organicFertiliserUsed"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.@id": "shortBareFallow"}
            ]
        },
        "none": {
            "siteType": ["glass or high accessible cover"]
        }
    }
}
LOOKUPS = {
    "crop": "IPCC_LAND_USE_CATEGORY",
    "landCover": [
        "IPCC_LAND_USE_CATEGORY",
        "LOW_RESIDUE_PRODUCING_CROP",
        "N_FIXING_CROP"
    ],
    "landUseManagement": "PRACTICE_INCREASING_C_INPUT",
    "soilType": "IPCC_SOIL_CATEGORY",
    "tillage": "IPCC_TILLAGE_MANAGEMENT_CATEGORY",
    "usdaSoilType": "IPCC_SOIL_CATEGORY"
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "statsDefinition": "simulated",
        "observations": "",
        "dates": "",
        "depthUpper": "0",
        "depthLower": "30",
        "methodClassification": "tier 1 model"
    }]
}

TERM_ID = 'organicCarbonPerHa'
_METHOD_CLASSIFICATION = MeasurementMethodClassification.TIER_1_MODEL.value

_CLAY_CONTENT_TERM_ID = "clayContent"
_SAND_CONTENT_TERM_ID = "sandContent"
_LONG_FALLOW_CROP_TERM_ID = "longFallowCrop"
_IMPROVED_PASTURE_TERM_ID = "improvedPasture"
_SHORT_BARE_FALLOW_TERM_ID = "shortBareFallow"
_ANIMAL_MANURE_USED_TERM_ID = "animalManureUsed"
_INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID = "inorganicNitrogenFertiliserUsed"
_ORGANIC_FERTILISER_USED_TERM_ID = "organicFertiliserUsed"
_SOIL_AMENDMENT_USED_TERM_ID = "amendmentIncreasingSoilCarbonUsed"

_CLAY_CONTENT_MAX = 8
_SAND_CONTENT_MIN = 70

_EQUILIBRIUM_TRANSITION_PERIOD = 20
"""
The number of years required for soil organic carbon to reach equilibrium after
a change in land use, management regime or carbon input regime.
"""

_EXCLUDED_ECO_CLIMATE_ZONES = {EcoClimateZone.POLAR_MOIST, EcoClimateZone.POLAR_DRY}

_VALID_SITE_TYPES = {
    SiteSiteType.CROPLAND.value,
    SiteSiteType.FOREST.value,
    SiteSiteType.OTHER_NATURAL_VEGETATION.value,
    SiteSiteType.PERMANENT_PASTURE.value
}


def _measurement(
    timestamps: list[int],
    descriptive_stats_dict: dict
) -> dict:
    """
    Build a HESTIA `Measurement` node to contain a value and descriptive statistics calculated by the models.

    The `descriptive_stats_dict` parameter should include the following keys and values from the
    [Measurement](https://hestia.earth/schema/Measurement) schema:
    ```
    {
        "value": list[float],
        "sd": list[float],
        "min": list[float],
        "max": list[float],
        "statsDefinition": str,
        "observations": list[int]
    }
    ```

    Parameters
    ----------
    timestamps : list[int]
        A list of calendar years associated to the calculated SOC stocks.
    descriptive_stats_dict : dict
        A dict containing the descriptive statistics data that should be added to the node.

    Returns
    -------
    dict
        A valid HESTIA `Measurement` node, see: https://www.hestia.earth/schema/Measurement.
    """
    measurement = _new_measurement(TERM_ID, MODEL) | descriptive_stats_dict
    measurement["dates"] = [f"{year}-12-31" for year in timestamps]
    measurement["depthUpper"] = DEPTH_UPPER
    measurement["depthLower"] = DEPTH_LOWER
    measurement["methodClassification"] = _METHOD_CLASSIFICATION
    return measurement


class _InventoryKey(Enum):
    """
    Enum representing the inner keys of the annual inventory is constructed from `Site` data.
    """
    LU_CATEGORY = "ipcc-land-use-category"
    MG_CATEGORY = "ipcc-management-category"
    CI_CATEGORY = "ipcc-carbon-input-category"
    SHOULD_RUN = "should-run-tier-1"


_REQUIRED_KEYS = {
    _InventoryKey.LU_CATEGORY,
    _InventoryKey.MG_CATEGORY,
    _InventoryKey.CI_CATEGORY
}
"""
The `_InventoryKey`s that must have valid values for an inventory year to be included in the model.
"""


_SOC_REFS = {
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 64000, "uncertainty": 5, "observations": 489},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 24000, "uncertainty": 5, "observations": 781},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 81000, "uncertainty": 5, "observations": 334},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 43000, "uncertainty": 8, "observations": 177},
        EcoClimateZone.POLAR_MOIST: {"value": 59000, "uncertainty": 41, "observations": 24},
        EcoClimateZone.POLAR_DRY: {"value": 59000, "uncertainty": 41, "observations": 24},
        EcoClimateZone.BOREAL_MOIST: {"value": 63000, "uncertainty": 18, "observations": 35},
        EcoClimateZone.BOREAL_DRY: {"value": 63000, "uncertainty": 18, "observations": 35},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 51000, "uncertainty": 10, "observations": 114},
        EcoClimateZone.TROPICAL_WET: {"value": 60000, "uncertainty": 8, "observations": 137},
        EcoClimateZone.TROPICAL_MOIST: {"value": 40000, "uncertainty": 7, "observations": 226},
        EcoClimateZone.TROPICAL_DRY: {"value": 21000, "uncertainty": 5, "observations": 554}
    },
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 55000, "uncertainty": 8, "observations": 183},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 19000, "uncertainty": 16, "observations": 41},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 76000, "uncertainty": 51, "observations": 6},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 33000, "uncertainty": 90},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 44000, "uncertainty": 11, "observations": 84},
        EcoClimateZone.TROPICAL_WET: {"value": 52000, "uncertainty": 6, "observations": 271},
        EcoClimateZone.TROPICAL_MOIST: {"value": 38000, "uncertainty": 5, "observations": 326},
        EcoClimateZone.TROPICAL_DRY: {"value": 19000, "uncertainty": 10, "observations": 135}
    },
    IpccSoilCategory.SANDY_SOILS: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 36000, "uncertainty": 23, "observations": 39},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 10000, "uncertainty": 5, "observations": 338},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 51000, "uncertainty": 13, "observations": 126},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 13000, "uncertainty": 33, "observations": 10},
        EcoClimateZone.POLAR_MOIST: {"value": 27000, "uncertainty": 67, "observations": 18},
        EcoClimateZone.POLAR_DRY: {"value": 27000, "uncertainty": 67, "observations": 18},
        EcoClimateZone.BOREAL_MOIST: {"value": 10000, "uncertainty": 90},
        EcoClimateZone.BOREAL_DRY: {"value": 10000, "uncertainty": 90},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 52000, "uncertainty": 34, "observations": 11},
        EcoClimateZone.TROPICAL_WET: {"value": 46000, "uncertainty": 20, "observations": 43},
        EcoClimateZone.TROPICAL_MOIST: {"value": 27000, "uncertainty": 12, "observations": 76},
        EcoClimateZone.TROPICAL_DRY: {"value": 9000, "uncertainty": 9, "observations": 164}
    },
    IpccSoilCategory.SPODIC_SOILS: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 143000, "uncertainty": 30, "observations": 9},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 128000, "uncertainty": 14, "observations": 45},
        EcoClimateZone.BOREAL_MOIST: {"value": 117000, "uncertainty": 90},
        EcoClimateZone.BOREAL_DRY: {"value": 117000, "uncertainty": 90}
    },
    IpccSoilCategory.VOLCANIC_SOILS: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 138000, "uncertainty": 12, "observations": 42},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 84000, "uncertainty": 65, "observations": 10},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 136000, "uncertainty": 14, "observations": 28},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 20000, "uncertainty": 90},
        EcoClimateZone.BOREAL_MOIST: {"value": 20000, "uncertainty": 90},
        EcoClimateZone.BOREAL_DRY: {"value": 20000, "uncertainty": 90},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 96000, "uncertainty": 31, "observations": 10},
        EcoClimateZone.TROPICAL_WET: {"value": 77000, "uncertainty": 27, "observations": 14},
        EcoClimateZone.TROPICAL_MOIST: {"value": 70000, "uncertainty": 90},
        EcoClimateZone.TROPICAL_DRY: {"value": 50000, "uncertainty": 90}
    },
    IpccSoilCategory.WETLAND_SOILS: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 135000, "uncertainty": 28, "observations": 28},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 74000, "uncertainty": 17, "observations": 49},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 128000, "uncertainty": 13, "observations": 42},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 87000, "uncertainty": 90},
        EcoClimateZone.BOREAL_MOIST: {"value": 116000, "uncertainty": 65, "observations": 6},
        EcoClimateZone.BOREAL_DRY: {"value": 116000, "uncertainty": 65, "observations": 6},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 82000, "uncertainty": 50, "observations": 12},
        EcoClimateZone.TROPICAL_WET: {"value": 49000, "uncertainty": 19, "observations": 33},
        EcoClimateZone.TROPICAL_MOIST: {"value": 68000, "uncertainty": 17, "observations": 55},
        EcoClimateZone.TROPICAL_DRY: {"value": 22000, "uncertainty": 17, "observations": 32}
    }
}

_LAND_USE_FACTORS = {
    IpccLandUseCategory.PERENNIAL_CROPS: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 0.72, "error": 22},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 0.72, "error": 22},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 0.72, "error": 22},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 0.72, "error": 22},
        EcoClimateZone.BOREAL_MOIST: {"value": 0.72, "error": 22},
        EcoClimateZone.BOREAL_DRY: {"value": 0.72, "error": 22},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 1.1, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 1.1, "error": 25},
        EcoClimateZone.TROPICAL_MOIST: {"value": 1.1, "error": 25},
        EcoClimateZone.TROPICAL_DRY: {"value": 1.1, "error": 25}
    },
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 1.35, "error": 4},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 1.35, "error": 4},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 1.35, "error": 4},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 1.35, "error": 4},
        EcoClimateZone.BOREAL_MOIST: {"value": 1.35, "error": 4},
        EcoClimateZone.BOREAL_DRY: {"value": 1.35, "error": 4},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 1.35, "error": 4},
        EcoClimateZone.TROPICAL_WET: {"value": 1.35, "error": 4},
        EcoClimateZone.TROPICAL_MOIST: {"value": 1.35, "error": 4},
        EcoClimateZone.TROPICAL_DRY: {"value": 1.35, "error": 4}
    },
    IpccLandUseCategory.ANNUAL_CROPS_WET: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 0.71, "error": 41},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 0.71, "error": 41},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 0.71, "error": 41},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 0.71, "error": 41},
        EcoClimateZone.BOREAL_MOIST: {"value": 0.71, "error": 41},
        EcoClimateZone.BOREAL_DRY: {"value": 0.71, "error": 41},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 0.86, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 0.83, "error": 11},
        EcoClimateZone.TROPICAL_MOIST: {"value": 0.83, "error": 11},
        EcoClimateZone.TROPICAL_DRY: {"value": 0.92, "error": 13}
    },
    IpccLandUseCategory.ANNUAL_CROPS: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 0.69, "error": 16},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 0.76, "error": 12},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 0.70, "error": 12},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 0.77, "error": 14},
        EcoClimateZone.BOREAL_MOIST: {"value": 0.70, "error": 12},
        EcoClimateZone.BOREAL_DRY: {"value": 0.77, "error": 14},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 0.86, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 0.83, "error": 11},
        EcoClimateZone.TROPICAL_MOIST: {"value": 0.83, "error": 11},
        EcoClimateZone.TROPICAL_DRY: {"value": 0.92, "error": 13}
    },
    IpccLandUseCategory.SET_ASIDE: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 0.82, "error": 17},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 0.93, "error": 11},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 0.82, "error": 17},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 0.93, "error": 11},
        EcoClimateZone.BOREAL_MOIST: {"value": 0.82, "error": 17},
        EcoClimateZone.BOREAL_DRY: {"value": 0.93, "error": 11},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 0.88, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 0.82, "error": 17},
        EcoClimateZone.TROPICAL_MOIST: {"value": 0.82, "error": 17},
        EcoClimateZone.TROPICAL_DRY: {"value": 0.93, "error": 11}
    }
}

_MANAGEMENT_FACTORS = {
    IpccManagementCategory.SEVERELY_DEGRADED: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 0.7, "error": 40},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 0.7, "error": 40},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 0.7, "error": 40},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 0.7, "error": 40},
        EcoClimateZone.BOREAL_MOIST: {"value": 0.7, "error": 40},
        EcoClimateZone.BOREAL_DRY: {"value": 0.7, "error": 40},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 0.7, "error": 40},
        EcoClimateZone.TROPICAL_WET: {"value": 0.7, "error": 40},
        EcoClimateZone.TROPICAL_MOIST: {"value": 0.7, "error": 40},
        EcoClimateZone.TROPICAL_DRY: {"value": 0.7, "error": 40}
    },
    IpccManagementCategory.IMPROVED_GRASSLAND: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 1.14, "error": 11},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 1.14, "error": 11},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 1.14, "error": 11},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 1.14, "error": 11},
        EcoClimateZone.BOREAL_MOIST: {"value": 1.14, "error": 11},
        EcoClimateZone.BOREAL_DRY: {"value": 1.14, "error": 11},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 1.16, "error": 40},
        EcoClimateZone.TROPICAL_WET: {"value": 1.17, "error": 9},
        EcoClimateZone.TROPICAL_MOIST: {"value": 1.17, "error": 9},
        EcoClimateZone.TROPICAL_DRY: {"value": 1.17, "error": 9}
    },
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 0.9, "error": 8},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 0.9, "error": 8},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 0.9, "error": 8},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 0.9, "error": 8},
        EcoClimateZone.BOREAL_MOIST: {"value": 0.9, "error": 8},
        EcoClimateZone.BOREAL_DRY: {"value": 0.9, "error": 8},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 0.9, "error": 8},
        EcoClimateZone.TROPICAL_WET: {"value": 0.9, "error": 8},
        EcoClimateZone.TROPICAL_MOIST: {"value": 0.9, "error": 8},
        EcoClimateZone.TROPICAL_DRY: {"value": 0.9, "error": 8}
    },
    IpccManagementCategory.REDUCED_TILLAGE: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 1.05, "error": 4},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 0.99, "error": 3},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 1.04, "error": 4},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 0.98, "error": 5},
        EcoClimateZone.BOREAL_MOIST: {"value": 1.04, "error": 4},
        EcoClimateZone.BOREAL_DRY: {"value": 0.98, "error": 5},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 1.02, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 1.04, "error": 7},
        EcoClimateZone.TROPICAL_MOIST: {"value": 1.04, "error": 7},
        EcoClimateZone.TROPICAL_DRY: {"value": 0.99, "error": 7}
    },
    IpccManagementCategory.NO_TILLAGE: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 1.1, "error": 4},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 1.04, "error": 3},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 1.09, "error": 4},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 1.03, "error": 4},
        EcoClimateZone.BOREAL_MOIST: {"value": 1.09, "error": 4},
        EcoClimateZone.BOREAL_DRY: {"value": 1.03, "error": 4},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 1.08, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 1.1, "error": 5},
        EcoClimateZone.TROPICAL_MOIST: {"value": 1.1, "error": 5},
        EcoClimateZone.TROPICAL_DRY: {"value": 1.04, "error": 7}
    }
}

_CARBON_INPUT_FACTORS = {
    IpccCarbonInputCategory.GRASSLAND_HIGH: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 1.11, "error": 7},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 1.11, "error": 7},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 1.11, "error": 7},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 1.11, "error": 7},
        EcoClimateZone.BOREAL_MOIST: {"value": 1.11, "error": 7},
        EcoClimateZone.BOREAL_DRY: {"value": 1.11, "error": 7},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 1.11, "error": 7},
        EcoClimateZone.TROPICAL_WET: {"value": 1.11, "error": 7},
        EcoClimateZone.TROPICAL_MOIST: {"value": 1.11, "error": 7},
        EcoClimateZone.TROPICAL_DRY: {"value": 1.11, "error": 7}
    },
    IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 1.44, "error": 13},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 1.37, "error": 12},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 1.44, "error": 13},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 1.37, "error": 12},
        EcoClimateZone.BOREAL_MOIST: {"value": 1.44, "error": 13},
        EcoClimateZone.BOREAL_DRY: {"value": 1.37, "error": 12},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 1.41, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 1.44, "error": 13},
        EcoClimateZone.TROPICAL_MOIST: {"value": 1.44, "error": 13},
        EcoClimateZone.TROPICAL_DRY: {"value": 1.37, "error": 12}
    },
    IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 1.11, "error": 10},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 1.04, "error": 13},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 1.11, "error": 10},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 1.04, "error": 13},
        EcoClimateZone.BOREAL_MOIST: {"value": 1.11, "error": 10},
        EcoClimateZone.BOREAL_DRY: {"value": 1.04, "error": 13},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 1.08, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 1.11, "error": 10},
        EcoClimateZone.TROPICAL_MOIST: {"value": 1.11, "error": 10},
        EcoClimateZone.TROPICAL_DRY: {"value": 1.04, "error": 13}
    },
    IpccCarbonInputCategory.CROPLAND_LOW: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: {"value": 0.92, "error": 14},
        EcoClimateZone.WARM_TEMPERATE_DRY: {"value": 0.95, "error": 13},
        EcoClimateZone.COOL_TEMPERATE_MOIST: {"value": 0.92, "error": 14},
        EcoClimateZone.COOL_TEMPERATE_DRY: {"value": 0.95, "error": 13},
        EcoClimateZone.BOREAL_MOIST: {"value": 0.92, "error": 14},
        EcoClimateZone.BOREAL_DRY: {"value": 0.95, "error": 13},
        EcoClimateZone.TROPICAL_MONTANE: {"value": 0.94, "error": 50},
        EcoClimateZone.TROPICAL_WET: {"value": 0.92, "error": 14},
        EcoClimateZone.TROPICAL_MOIST: {"value": 0.92, "error": 14},
        EcoClimateZone.TROPICAL_DRY: {"value": 0.95, "error": 13}
    }
}

_KWARGS_TO_SAMPLE_FUNC = {
    ("value", "uncertainty"): sample_plus_minus_uncertainty,
    ("value", "error"): sample_plus_minus_error,
    ("value",): sample_constant
}

_IPCC_CATEGORY_TO_FACTOR_DICT = {
    IpccSoilCategory: _SOC_REFS,
    IpccLandUseCategory: _LAND_USE_FACTORS,
    IpccManagementCategory: _MANAGEMENT_FACTORS,
    IpccCarbonInputCategory: _CARBON_INPUT_FACTORS
}


def _sample_parameter(
    iterations: int,
    parameter: Union[IpccSoilCategory, IpccLandUseCategory, IpccManagementCategory, IpccCarbonInputCategory],
    eco_climate_zone: EcoClimateZone,
    seed: Union[int, random.Generator, None] = None
) -> NDArray:
    """
    Sample a model parameter (SOC ref or stock change factor) using the function specified in `KWARGS_TO_SAMPLE_FUNC`.

    Parameters
    ----------
    iterations : int
        The number of samples to take.
    parameter : IpccSoilCategory | IpccLandUseCategory | IpccManagementCategory | IpccCarbonInputCategory
        The model parameter to sample.
    eco_climate_zone : EcoClimateZone
        The eco-climate zone of the site.
    seed : int | Generator | None, optional
        A seed to initialize the BitGenerator. If passed a Generator, it will be returned unaltered. If `None`, then
        fresh, unpredictable entropy will be pulled from the OS.

    Returns
    -------
    NDArray
        The sampled parameter as a numpy array with shape `(1, iterations)`.
    """
    parameter_dict = _IPCC_CATEGORY_TO_FACTOR_DICT.get(type(parameter))
    kwargs = parameter_dict.get(parameter, {}).get(eco_climate_zone, {"value": 1})
    func = _get_sample_func(kwargs)
    return func(iterations=iterations, seed=seed, **kwargs)


def _get_sample_func(kwargs: dict) -> Callable:
    """
    Select the correct sample function for a parameter based on the distribution data available. All possible
    parameters for the model should have, at a minimum, a `value`, meaning that no default function needs to be
    specified.

    This function has been extracted into it's own method to allow for mocking of sample function.

    Keyword Args
    ------------
    value : float
        The distribution mean.
    uncertainty : float
        The +/- uncertainty of the 95% confidence interval expressed as a percentge of the mean.
    error : float
        Two standard deviations expressed as a percentage of the mean.

    Returns
    -------
    Callable
        The sample function for the distribution.
    """
    return next(
        sample_func for required_kwargs, sample_func in _KWARGS_TO_SAMPLE_FUNC.items()
        if all(kwarg in kwargs.keys() for kwarg in required_kwargs)
    )


def _get_soc_ref_preview(ipcc_soil_category: IpccSoilCategory, eco_climate_zone: EcoClimateZone) -> Union[float, None]:
    """
    Retrieve the mean value of the SOC ref for a specific combination of `IpccSoilCategory` and `EcoClimateZone`. This
    is primarily for logging purposes.

    Parameters
    ----------
    ipcc_soil_category : IpccSoilCategory
    eco_climate_zone: EcoClimateZone

    Returns
    -------
    float | None
        The mean value SOC ref or `None` if no reference value is available.
    """
    return _SOC_REFS.get(ipcc_soil_category, {}).get(eco_climate_zone, {}).get("value", None)


# --- TIER 1 MODEL ---


def should_run(site: dict) -> tuple[bool, dict, dict]:
    """
    Extract data from site & related cycles, pre-process data and determine whether there is sufficient data to run the
    Tier 1 model.

    The returned `inventory` should be a dict with the shape:
    ```
    {
        year (int): {
            _InventoryKey.SHOULD_RUN: bool,
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory
        },
        ...
    }
    ```

    The returned `kwargs` should be a dict with the shape:
    ```
    {
        "eco_climate_zone": int,
        "ipcc_soil_category": IpccSoilCategory,
        "soc_ref": float
    }
    ```

    Parameters
    ----------
    site : dict
        A HESTIA `Site` node, see: https://www.hestia.earth/schema/Site.

    Returns
    -------
    tuple[bool, dict, dict]
        A tuple containing `(should_run_, inventory, kwargs, logs)`.
    """
    site_type = site.get("siteType", "")
    management_nodes = get_valid_management_nodes(site)
    measurement_nodes = site.get("measurements", [])

    eco_climate_zone = get_eco_climate_zone_value(site, as_enum=True)
    ipcc_soil_category = _assign_ipcc_soil_category(measurement_nodes)
    soc_ref = _get_soc_ref_preview(ipcc_soil_category, eco_climate_zone)

    has_management = len(management_nodes) > 0
    has_measurements = len(measurement_nodes) > 0

    should_compile_inventory = all([
        site_type in _VALID_SITE_TYPES,
        eco_climate_zone not in _EXCLUDED_ECO_CLIMATE_ZONES,
        soc_ref or -9999 > 0,
        has_management,
        has_measurements
    ])

    inventory, inventory_logs = (
        _compile_inventory(
            site_type,
            management_nodes,
            ipcc_soil_category
        ) if should_compile_inventory else ({}, {})
    )

    kwargs = {
        "seed": gen_seed(site, MODEL, TERM_ID),
        "eco_climate_zone": eco_climate_zone,
        "ipcc_soil_category": ipcc_soil_category,
    }

    should_run_ = any(
        year for year, group in inventory.items() if group.get(_InventoryKey.SHOULD_RUN)
    )

    logs = inventory_logs | {
        "site_type": site_type,
        "soc_ref": soc_ref,
        "has_management": has_management,
        "has_measurements": has_measurements,
        "should_compile_inventory_tier_1": should_compile_inventory,
        "should_run_tier_1": should_run_
    }

    return should_run_, inventory, kwargs, logs


def get_valid_management_nodes(site: dict) -> list[dict]:
    """Retrieve valid mangement nodes from a site."""
    return [node for node in site.get("management", []) if validate_start_date_end_date(node)]


def run(
    inventory: dict,
    *,
    eco_climate_zone: EcoClimateZone,
    ipcc_soil_category: IpccSoilCategory,
    iterations: int,
    seed: Union[int, random.Generator, None] = None,
    **_
) -> list[dict]:
    """
    Run the IPCC (2019) Tier 1 methodology for calculating SOC stocks (in kg C ha-1) for each year in the inventory
    and wrap each of the calculated values in HESTIA measurement nodes. To avoid any errors, the `inventory` parameter
    must be pre-validated by the `should_run` function.

    See [IPCC (2019) Vol. 4, Ch. 2](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more information.

    The inventory should be in the following shape:
    ```
    {
        year (int): {
            _InventoryKey.SHOULD_RUN: bool,
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory
        },
        ...
    }
    ```

    Parameters
    ----------
    inventory : dict
        The inventory built by the `_should_run` function.
    eco_climate_zone : EcoClimateZone
        The eco-climate zone of the site.
    ipcc_soil_category : IpccSoilCategory
        The IPCC soil category of the site.
    iterations : int
        Number of iterations to run the model for.
    seed : int | Generator | None, optional
        A seed to initialize the BitGenerator. If passed a Generator, it will be returned unaltered. If `None`, then
        fresh, unpredictable entropy will be pulled from the OS.

    Returns
    -------
    list[dict]
        A list of HESTIA nodes containing model output results.
    """

    valid_inventory = {
        year: group for year, group in inventory.items() if group.get(_InventoryKey.SHOULD_RUN)
    }

    complete_inventory = dict(sorted(
        merge(valid_inventory, _calc_missing_equilibrium_years(valid_inventory)).items()
    ))

    timestamps = [year for year in complete_inventory.keys()]
    land_use_categories = [group[_InventoryKey.LU_CATEGORY] for group in complete_inventory.values()]
    management_categories = [group[_InventoryKey.MG_CATEGORY] for group in complete_inventory.values()]
    carbon_input_categories = [group[_InventoryKey.CI_CATEGORY] for group in complete_inventory.values()]

    regime_start_years = _calc_regime_start_years(complete_inventory)

    rng = random.default_rng(seed)

    soc_ref = _sample_parameter(iterations, ipcc_soil_category, eco_climate_zone, seed=rng)
    land_use_factors = _get_factor_annual(iterations, land_use_categories, eco_climate_zone, seed=rng)
    management_factors = _get_factor_annual(iterations, management_categories, eco_climate_zone, seed=rng)
    carbon_input_factors = _get_factor_annual(iterations, carbon_input_categories, eco_climate_zone, seed=rng)

    soc_equilibriums = _calc_soc_equilibrium(soc_ref, land_use_factors, management_factors, carbon_input_factors)
    soc_stocks = _calc_soc_stocks(timestamps, regime_start_years, soc_equilibriums)

    descriptive_stats = calc_descriptive_stats(
        soc_stocks,
        STATS_DEFINITION,
        axis=1,     # Calculate stats rowwise.
        decimals=6  # Round values to the nearest milligram.
    )

    return [_measurement(timestamps, descriptive_stats)]


def _calc_missing_equilibrium_years(inventory: dict) -> dict:
    """
    Calculate any missing inventory years where SOC would have reached equilibrium and return them as a dict.

    Parameters
    ----------
    inventory : dict

    Returns
    -------
    dict
        A dictionary of missing equilibrium years with the same structure as `inventory`.
    """

    min_year, max_year = min(inventory.keys()), max(inventory.keys())

    def add_missing_equilibrium_year(missing_years: dict, year: int):
        group = inventory[year]
        existing_years = set(list(inventory.keys()) + list(missing_years.keys()))

        regime_start_year = _calc_regime_start_year(year, inventory)
        equilibrium_year = regime_start_year + _EQUILIBRIUM_TRANSITION_PERIOD

        should_add_equilibrium = (
            min_year < equilibrium_year < max_year      # Is the year relevant?
            and equilibrium_year not in existing_years  # Is the year missing?
            and not any(year_ in existing_years for year_ in range(year+1, equilibrium_year))  # Is the year superseded?
        )

        if should_add_equilibrium:
            missing_years[equilibrium_year] = group

        return missing_years

    missing_years = reduce(add_missing_equilibrium_year, inventory.keys(), dict())

    return missing_years


def _calc_regime_start_years(inventory: dict):
    """
    Calculate when the land-use and land-management regime of all inventory years began.

    Parameters
    ----------
    inventory : dict

    Returns
    -------
    list[int]
    """
    return [_calc_regime_start_year(year, inventory) for year in inventory.keys()]


def _calc_regime_start_year(current_year: int, inventory: dict) -> int:
    """
    Calculate when the land-use and land-management regime of a specific inventory year began.

    Parameters
    ----------
    current_year : int
    inventory : dict

    Returns
    -------
    int
    """
    MATCH_KEYS = {_InventoryKey.LU_CATEGORY, _InventoryKey.MG_CATEGORY, _InventoryKey.CI_CATEGORY}
    previous_years = list(reversed([year for year in inventory.keys() if year <= current_year]))
    return next(
        (
            previous_years[i-1] for i, previous_year in enumerate(previous_years)
            if not all([
                inventory[current_year][key] == inventory[previous_year][key]
                for key in MATCH_KEYS
            ])
        ),
        previous_years[-1] - _EQUILIBRIUM_TRANSITION_PERIOD
    )


def _get_factor_annual(
    iterations: int,
    category_annual: list[Union[IpccLandUseCategory, IpccManagementCategory, IpccCarbonInputCategory]],
    eco_climate_zone: EcoClimateZone,
    seed: Optional[int] = None
) -> NDArray:
    """
    Build an numpy array with the shape `(len(category_annual), iterations)`, where each row represents an inventory
    year and each column contains a sampled value for that year's factor. All rows representing the same factor should
    be identical.

    Parameters
    ----------
    iterations : int
        The number of samples to take for each year.
    category_annual : list[IpccLandUseCategory | IpccManagementCategory | IpccCarbonInputCategory]
        A list of annual IPCC categories that are linked to SOC stock change factors.
    eco_climate_zone : EcoClimateZone
        The eco-climate zone of the site.
    seed : int | None
        An optional seed for the random sampling of model parameters. If `None`, then fresh, unpredictable entropy will
        be pulled from the OS.

    Returns
    -------
    NDArray
        The sampled factors as a numpy array.
    """
    param_cache = {
        category: _sample_parameter(iterations, category, eco_climate_zone, seed=seed)
        for category in sorted(set(category_annual), key=lambda category: category.value)
    }
    return vstack([param_cache[category] for category in category_annual])


def _calc_soc_equilibrium(
    soc_ref: NDArray,
    land_use_factor: NDArray,
    management_factor: NDArray,
    carbon_input_factor: NDArray
) -> NDArray:
    """
    Calculate the soil organic carbon (SOC) equilibrium based on reference SOC and factors.

    In the tier 1 model, SOC equilibriums are considered to be reached after 20 years of consistant land use,
    management and carbon input.

    Parameters
    ----------
    soc_ref : NDArray
        The reference condition SOC stock in the 0-30cm depth interval, kg C ha-1.
    land_use_factor : NDArray
        The stock change factor for mineral soil organic C land-use systems or sub-systems
        for a particular land-use, dimensionless.
    management_factor : NDArray
        The stock change factor for mineral soil organic C for management regime, dimensionless.
    carbon_input_factor : NDArray
        The stock change factor for mineral soil organic C for the input of organic amendments, dimensionless.

    Returns
    -------
    NDArray
        The calculated SOC equilibrium, kg C ha-1.
    """
    return soc_ref * land_use_factor * management_factor * carbon_input_factor


def _calc_soc_stocks(
    timestamps: list[int],
    regime_start_years: list[int],
    soc_equilibriums: NDArray
) -> NDArray:
    """
    Calculate soil organic carbon (SOC) stocks (kg C ha-1) in the 0-30cm depth interval for each year in the inventory.

    Parameters
    ----------
    timestamps : list[int]
        A list of timestamps for each year in the inventory.
    regime_start_years : list[int]
        A pre-calculated list of the regime start year for each year in the inventory.
    soc_equilibriums : NDArray
        A numpy array of SOC equilibriums where each row represents a different calendar year.

    Returns
    -------
    NDArray
        SOC stocks for each year in the inventory.
    """
    soc_stocks = empty_like(soc_equilibriums)
    soc_stocks[0] = soc_equilibriums[0]

    for index in range(1, len(timestamps)):

        current_year = timestamps[index]
        current_soc_equilibrium = soc_equilibriums[index]
        current_regime_start_year = regime_start_years[index]

        previous_index = (
            timestamps.index(current_regime_start_year) - 1 if current_regime_start_year in timestamps else 0
        )
        previous_year = timestamps[previous_index]
        previous_soc_stock = soc_stocks[previous_index]

        regime_duration = current_year - previous_year
        time_ratio = min(regime_duration / _EQUILIBRIUM_TRANSITION_PERIOD, 1)
        soc_delta = (current_soc_equilibrium - previous_soc_stock) * time_ratio

        soc_stocks[index] = previous_soc_stock + soc_delta

    return soc_stocks


# --- COMPILE TIER 1 INVENTORY ---


def _compile_inventory(
    site_type: str, management_nodes: list[dict], ipcc_soil_category: IpccSoilCategory
) -> tuple[dict, dict]:
    """
    Builds an annual inventory of data and a dictionary of keyword arguments for the tier 1 model.

    Parameters
    ----------
    site_id : str
        The `@id` of the site.
    site_type : str
        A valid [site type](https://hestia.earth/schema/Site#siteType).
    management_nodes : list[dict]
        A list of [Management nodes](https://hestia.earth/schema/Management).
    ipcc_soil_category : IpccSoilCategory
        The site's assigned IPCC soil category.

    Returns
    -------
    tuple[dict, dict]
        A tuple containing `(inventory, logs)`.
    """
    grouped_management = group_nodes_by_year(management_nodes)

    # If no `landCover` nodes in `site.management` use `site.siteType` to assign static `IpccLandUseCategory`.
    run_with_site_type = len(filter_list_term_type(management_nodes, [TermTermType.LANDCOVER])) == 0
    site_type_ipcc_land_use_category = SITE_TYPE_TO_IPCC_LAND_USE_CATEGORY.get(site_type, IpccLandUseCategory.UNKNOWN)

    grouped_management = group_nodes_by_year(management_nodes)

    grouped_land_use_categories = {
        year: {
            _InventoryKey.LU_CATEGORY: (
                site_type_ipcc_land_use_category if run_with_site_type
                else _assign_ipcc_land_use_category(nodes, ipcc_soil_category)
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_management_categories = {
        year: {
            _InventoryKey.MG_CATEGORY: _assign_ipcc_management_category(
                nodes,
                grouped_land_use_categories[year][_InventoryKey.LU_CATEGORY]
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_carbon_input_categories = {
        year: {
            _InventoryKey.CI_CATEGORY: _assign_ipcc_carbon_input_category(
                nodes,
                grouped_management_categories[year][_InventoryKey.MG_CATEGORY]
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_data = merge(
        grouped_land_use_categories,
        grouped_management_categories,
        grouped_carbon_input_categories
    )

    grouped_should_run = {
        year: {_InventoryKey.SHOULD_RUN: _should_run_inventory_year(group)}
        for year, group in grouped_data.items()
    }

    inventory = merge(grouped_data, grouped_should_run)
    logs = {
        "run_with_site_type": run_with_site_type
    }

    return inventory, logs


def _assign_ipcc_soil_category(
    measurement_nodes: list[dict],
    default: IpccSoilCategory = IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS
) -> IpccSoilCategory:
    """
    Assign an IPCC soil category based on a site's measurement nodes.

    Parameters
    ----------
    measurement_nodes : list[dict]
        List of A list of [Measurement nodes](https://hestia.earth/schema/Measurement)..
    default : IpccSoilCategory, optional
        The default soil category if none matches, by default IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS.

    Returns
    -------
    IpccSoilCategory
        The assigned IPCC soil category.
    """
    soil_types = _get_soil_type_measurements(measurement_nodes, TermTermType.SOILTYPE)
    usda_soil_types = _get_soil_type_measurements(measurement_nodes, TermTermType.USDASOILTYPE)

    clay_content = get_node_value(find_term_match(measurement_nodes, _CLAY_CONTENT_TERM_ID))
    sand_content = get_node_value(find_term_match(measurement_nodes, _SAND_CONTENT_TERM_ID))

    has_sandy_soil = clay_content < _CLAY_CONTENT_MAX and sand_content > _SAND_CONTENT_MIN

    return next(
        (
            key for key in _SOIL_CATEGORY_DECISION_TREE
            if _SOIL_CATEGORY_DECISION_TREE[key](
                key=key,
                soil_types=soil_types,
                usda_soil_types=usda_soil_types,
                has_sandy_soil=has_sandy_soil
            )
        ),
        default
    ) if len(soil_types) > 0 or len(usda_soil_types) > 0 else default


def _get_soil_type_measurements(
    nodes: list[dict], term_type: Literal[TermTermType.SOILTYPE, TermTermType.USDASOILTYPE]
) -> list[dict]:
    grouped = group_by_term(filter_list_term_type(nodes, term_type))

    def depth_distance(node):
        upper, lower = node.get("depthUpper", 0), node.get("depthLower", 100)
        return abs(upper - DEPTH_UPPER) + abs(lower - DEPTH_LOWER)

    return non_empty_list(
        min(nodes_, key=depth_distance) for key in grouped if (nodes_ := grouped.get(key, []))
    )


def _check_soil_category(
    *,
    key: IpccSoilCategory,
    soil_types: list[dict],
    usda_soil_types: list[dict],
    **_
) -> bool:
    """
    Check if the soil category matches the given key.

    Parameters
    ----------
    key : IpccSoilCategory
        The IPCC soil category to check.
    soil_types : list[dict]
        List of soil type measurement nodes.
    usda_soil_types : list[dict]
        List of USDA soil type measurement nodes

    Returns
    -------
    bool
        `True` if the soil category matches, `False` otherwise.
    """
    SOIL_TYPE_LOOKUP = LOOKUPS["soilType"]
    USDA_SOIL_TYPE_LOOKUP = LOOKUPS["usdaSoilType"]

    target_lookup_values = IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_LOOKUP_VALUE.get(key, None)

    is_soil_type_match = cumulative_nodes_lookup_match(
        soil_types,
        lookup=SOIL_TYPE_LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    is_usda_soil_type_match = cumulative_nodes_lookup_match(
        usda_soil_types,
        lookup=USDA_SOIL_TYPE_LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    return is_soil_type_match or is_usda_soil_type_match


def _check_sandy_soil_category(
    *,
    key: IpccSoilCategory,
    soil_types: list[dict],
    usda_soil_types: list[dict],
    has_sandy_soil: bool,
    **_
) -> bool:
    """
    Check if the soils are sandy.

    This function is special case of `_check_soil_category`.

    Parameters
    ----------
    key : IpccSoilCategory
        The IPCC soil category to check.
    soil_types : list[dict]
        List of soil type measurement nodes.
    usda_soil_types : list[dict]
        List of USDA soil type measurement nodes
    has_sandy_soil : bool
        True if the soils are sandy, False otherwise.

    Returns
    -------
    bool
        `True` if the soil category matches, `False` otherwise.
    """
    return _check_soil_category(key=key, soil_types=soil_types, usda_soil_types=usda_soil_types) or has_sandy_soil


_SOIL_CATEGORY_DECISION_TREE = {
    IpccSoilCategory.ORGANIC_SOILS: _check_soil_category,
    IpccSoilCategory.SANDY_SOILS: _check_sandy_soil_category,
    IpccSoilCategory.WETLAND_SOILS: _check_soil_category,
    IpccSoilCategory.VOLCANIC_SOILS: _check_soil_category,
    IpccSoilCategory.SPODIC_SOILS: _check_soil_category,
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: _check_soil_category,
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: _check_soil_category
}
"""
A decision tree mapping IPCC soil categories to corresponding check functions.

Key: IpccSoilCategory
Value: Corresponding function for checking the match of the given soil category based on soil types.
"""


def _assign_ipcc_land_use_category(
    management_nodes: list[dict], ipcc_soil_category: IpccSoilCategory,
) -> IpccLandUseCategory:
    """
    Assigns IPCC land use category based on management nodes and soil category.

    Parameters
    ----------
    management_nodes : list[dict]
        List of management nodes.
    ipcc_soil_category : IpccSoilCategory
        The site"s assigned IPCC soil category.

    Returns
    -------
    IpccLandUseCategory
        Assigned IPCC land use category.
    """
    DECISION_TREE = _LAND_USE_CATEGORY_DECISION_TREE
    DEFAULT = IpccLandUseCategory.UNKNOWN

    cover_crop_nodes, land_cover_nodes = split_on_condition(
        filter_list_term_type(management_nodes, [TermTermType.LANDCOVER]),
        is_cover_crop
    )

    water_regime_nodes = filter_list_term_type(management_nodes, [TermTermType.WATERREGIME])

    has_irrigation = check_irrigation(water_regime_nodes)
    has_upland_rice = _has_upland_rice(land_cover_nodes)
    has_irrigated_upland_rice = has_upland_rice and has_irrigation
    has_long_fallow = _has_long_fallow(cover_crop_nodes)
    has_wetland_soils = ipcc_soil_category is IpccSoilCategory.WETLAND_SOILS

    should_run_ = land_cover_nodes or cover_crop_nodes

    return next(
        (
            key for key in DECISION_TREE
            if DECISION_TREE[key](
                key=key,
                land_cover_nodes=land_cover_nodes,
                has_long_fallow=has_long_fallow,
                has_irrigated_upland_rice=has_irrigated_upland_rice,
                has_wetland_soils=has_wetland_soils
            )
        ),
        DEFAULT
    ) if should_run_ else DEFAULT


def _has_upland_rice(land_cover_nodes: list[dict]) -> bool:
    """
    Check if upland rice is present in the land cover nodes.

    Parameters
    ----------
    land_cover_nodes : list[dict]
        List of land cover nodes to be checked.

    Returns
    -------
    bool
        `True` if upland rice is present, `False` otherwise.
    """
    return cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=get_upland_rice_land_cover_terms(),
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD
    )


def _has_long_fallow(land_cover_nodes: list[dict]) -> bool:
    """
    Check if long fallow terms are present in the land cover nodes.

    n.b., a super majority of the site area must be under long fallow for it to be classified as set aside.

    Parameters
    ----------
    land_cover_nodes : list[dict]
        List of land cover nodes to be checked.

    Returns
    -------
    bool
        `True` if long fallow is present, `False` otherwise.
    """
    return cumulative_nodes_match(
        lambda node: get_node_property(node, _LONG_FALLOW_CROP_TERM_ID, False).get("value", 0),
        land_cover_nodes,
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD
    )


def _check_ipcc_land_use_category(*, key: IpccLandUseCategory, land_cover_nodes: list[dict], **kwargs) -> bool:
    """
    Check if the land cover nodes and keyword args satisfy the requirements for the given key.

    Parameters
    ----------
    key : IpccLandUseCategory
        The IPCC land use category to check.
    land_cover_nodes : list[dict]
        List of land cover nodes to be checked.

    Keyword Args
    ------------
    has_irrigated_upland_rice : bool
        Indicates whether irrigated upland rice is present on more than 30% of the site.
    has_long_fallow : bool
        Indicates whether long fallow is present on more than 70% of the site.
    has_wetland_soils : bool
        Indicates whether wetland soils are present to more than 30% of the site.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.
    """
    LOOKUP = LOOKUPS["landCover"][0]
    target_lookup_values = IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE.get(key, None)
    valid_lookup = cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    validation_kwargs = _IPCC_LAND_USE_CATEGORY_TO_VALIDATION_KWARGS.get(key, set())
    valid_kwargs = all(v for k, v in kwargs.items() if k in validation_kwargs)

    override_kwargs = _IPCC_LAND_USE_CATEGORY_TO_OVERRIDE_KWARGS.get(key, set())
    valid_override = any(v for k, v in kwargs.items() if k in override_kwargs)

    return (valid_lookup and valid_kwargs) or valid_override


_IPCC_LAND_USE_CATEGORY_TO_VALIDATION_KWARGS = {
    IpccLandUseCategory.ANNUAL_CROPS_WET: {"has_wetland_soils"},
}
"""
Keyword arguments that need to be validated in addition to the `landCover` lookup match for specific
`IpccLandUseCategory`s.
"""

_IPCC_LAND_USE_CATEGORY_TO_OVERRIDE_KWARGS = {
    IpccLandUseCategory.SET_ASIDE: {"has_long_fallow"},
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: {"has_irrigated_upland_rice"}
}
"""
Keyword arguments that can override the `landCover` lookup match for specific `IpccLandUseCategory`s.
"""


_LAND_USE_CATEGORY_DECISION_TREE = {
    IpccLandUseCategory.GRASSLAND: _check_ipcc_land_use_category,
    IpccLandUseCategory.SET_ASIDE: _check_ipcc_land_use_category,
    IpccLandUseCategory.PERENNIAL_CROPS: _check_ipcc_land_use_category,
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: _check_ipcc_land_use_category,
    IpccLandUseCategory.ANNUAL_CROPS_WET: _check_ipcc_land_use_category,
    IpccLandUseCategory.ANNUAL_CROPS: _check_ipcc_land_use_category,
    IpccLandUseCategory.FOREST: _check_ipcc_land_use_category,
    IpccLandUseCategory.NATIVE: _check_ipcc_land_use_category,
    IpccLandUseCategory.OTHER: _check_ipcc_land_use_category
}
"""
A decision tree mapping IPCC soil categories to corresponding check functions.

Key: IpccLandUseCategory
Value: Corresponding function for checking the match of the given land use category based on land cover nodes
and additional kwargs.
"""


def _assign_ipcc_management_category(
    management_nodes: list[dict], ipcc_land_use_category: IpccLandUseCategory
) -> IpccManagementCategory:
    """
    Assign an IPCC Management Category based on the given management nodes and IPCC Land Use Category.

    Parameters
    ----------
    management_nodes : list[dict]
        List of management nodes.
    ipcc_land_use_category : IpccLandUseCategory
        The IPCC Land Use Category.

    Returns
    -------
    IpccManagementCategory
        The assigned IPCC Management Category.
    """
    decision_tree = _IPCC_LAND_USE_CATEGORY_TO_DECISION_TREE.get(ipcc_land_use_category, {})
    default = _IPCC_LAND_USE_CATEGORY_TO_DEFAULT_IPCC_MANAGEMENT_CATEGORY.get(
        ipcc_land_use_category, IpccManagementCategory.NOT_RELEVANT
    )

    land_cover_nodes = filter_list_term_type(management_nodes, [TermTermType.PASTUREMANAGEMENT])
    tillage_nodes = filter_list_term_type(management_nodes, [TermTermType.TILLAGE])

    should_run_ = any([
        decision_tree == _GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE and len(land_cover_nodes) > 0,
        decision_tree == _TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE and len(tillage_nodes) > 0
    ])

    return next(
        (
            key for key in decision_tree
            if decision_tree[key](
                key=key,
                land_cover_nodes=land_cover_nodes,
                tillage_nodes=tillage_nodes,
            )
        ),
        default
    ) if should_run_ else default


def _check_grassland_ipcc_management_category(
    *, key: IpccManagementCategory, land_cover_nodes: list[dict], **_
) -> bool:
    """
    Check if the land cover nodes match the target conditions for a grassland IpccManagementCategory.

    Parameters
    ----------
    key : IpccManagementCategory
        The IPCC management category to check.
    land_cover_nodes : list[dict]
        List of land cover nodes to be checked.

    Returns
    -------
    bool
        `True` if the conditions match the specified management category, `False` otherwise.
    """
    target_term_ids = IPCC_MANAGEMENT_CATEGORY_TO_GRASSLAND_MANAGEMENT_TERM_ID.get(key, None)
    return cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=target_term_ids,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )


_GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.SEVERELY_DEGRADED: _check_grassland_ipcc_management_category,
    IpccManagementCategory.IMPROVED_GRASSLAND: _check_grassland_ipcc_management_category,
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: _check_grassland_ipcc_management_category,
    IpccManagementCategory.NOMINALLY_MANAGED: _check_grassland_ipcc_management_category
}
"""
Decision tree mapping IPCC management categories to corresponding check functions for grassland.

Key: IpccManagementCategory
Value: Corresponding function for checking the match of the given management category based on land cover nodes.
"""


def _check_tillage_ipcc_management_category(
    *, key: IpccManagementCategory, tillage_nodes: list[dict], **_
) -> bool:
    """
    Check if the tillage nodes match the target conditions for a tillage IpccManagementCategory.

    Parameters
    ----------
    key : IpccManagementCategory
        The IPCC management category to check.
    tillage_nodes : list[dict]
        List of tillage nodes to be checked.

    Returns
    -------
    bool
        `True` if the conditions match the specified management category, `False` otherwise.
    """
    LOOKUP = LOOKUPS["tillage"]
    target_lookup_values = IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE.get(key, None)
    return cumulative_nodes_lookup_match(
        tillage_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )


_TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.FULL_TILLAGE: _check_tillage_ipcc_management_category,
    IpccManagementCategory.REDUCED_TILLAGE: _check_tillage_ipcc_management_category,
    IpccManagementCategory.NO_TILLAGE: _check_tillage_ipcc_management_category
}
"""
Decision tree mapping IPCC management categories to corresponding check functions for tillage.

Key: IpccManagementCategory
Value: Corresponding function for checking the match of the given management category based on tillage nodes.
"""


_IPCC_LAND_USE_CATEGORY_TO_DECISION_TREE = {
    IpccLandUseCategory.GRASSLAND: _GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE,
    IpccLandUseCategory.ANNUAL_CROPS_WET: _TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE,
    IpccLandUseCategory.ANNUAL_CROPS: _TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE
}
"""
Decision tree mapping IPCC land use categories to corresponding decision trees for management categories.

Key: IpccLandUseCategory
Value: Corresponding decision tree for IPCC management categories based on land use categories.
"""

_IPCC_LAND_USE_CATEGORY_TO_DEFAULT_IPCC_MANAGEMENT_CATEGORY = {
    IpccLandUseCategory.GRASSLAND: IpccManagementCategory.UNKNOWN,
    IpccLandUseCategory.ANNUAL_CROPS_WET: IpccManagementCategory.UNKNOWN,
    IpccLandUseCategory.ANNUAL_CROPS: IpccManagementCategory.UNKNOWN
}
"""
Mapping of default IPCC management categories for each IPCC land use category.

Key: IpccLandUseCategory
Value: Default IPCC management category for the given land use category.
"""


def _assign_ipcc_carbon_input_category(
    management_nodes: list[dict],
    ipcc_management_category: IpccManagementCategory
) -> IpccCarbonInputCategory:
    """
    Assigns an IPCC Carbon Input Category based on the provided management nodes and IPCC Management Category.

    Parameters
    ----------
    management_nodes : list[dict]
        List of management nodes containing information about land management practices.
    ipcc_management_category : IpccManagementCategory
        IPCC Management Category for which the Carbon Input Category needs to be assigned.

    Returns
    -------
    IpccCarbonInputCategory
        Assigned IPCC Carbon Input Category.
    """
    decision_tree = _DECISION_TREE_FROM_IPCC_MANAGEMENT_CATEGORY.get(ipcc_management_category, {})
    default = _DEFAULT_CARBON_INPUT_CATEGORY.get(
        ipcc_management_category, IpccCarbonInputCategory.NOT_RELEVANT
    )

    should_run_ = len(management_nodes) > 0

    return next(
        (key for key in decision_tree if decision_tree[key](
            key=key,
            **_get_carbon_input_kwargs(management_nodes)
        )),
        default
    ) if should_run_ else default


def _check_grassland_ipcc_carbon_input_category(
    *, key: IpccCarbonInputCategory, num_grassland_improvements: int, **_,
) -> bool:
    """
    Checks if the given carbon input arguments satisfy the conditions for a specific
    Grassland IPCC Carbon Input Category.

    Parameters
    ----------
    key : IpccCarbonInputCategory
        The grassland IPCC Carbon Input Category to check.
    num_grassland_improvements : int
        The number of grassland improvements.

    Returns
    -------
    bool
        `True` if the conditions for the specified category are met; otherwise, `False`.
    """
    return num_grassland_improvements >= _GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_TO_MIN_NUM_IMPROVEMENTS[key]


_GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_TO_MIN_NUM_IMPROVEMENTS = {
    IpccCarbonInputCategory.GRASSLAND_HIGH: 2,
    IpccCarbonInputCategory.GRASSLAND_MEDIUM: 0
}
"""
A mapping from IPCC Grassland Carbon Input Categories to the minimum number of improvements required.

Key: IpccCarbonInputCategory
Value: Minimum number of improvements required for the corresponding Grassland Carbon Input Category.
"""


_GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE = {
    IpccCarbonInputCategory.GRASSLAND_HIGH: _check_grassland_ipcc_carbon_input_category,
    IpccCarbonInputCategory.GRASSLAND_MEDIUM: _check_grassland_ipcc_carbon_input_category
}
"""
A decision tree for assigning IPCC Carbon Input Categories to Grassland based on the number of improvements.

Key: IpccCarbonInputCategory
Value: Corresponding function to check if the given conditions are met for the category.
"""


def _check_cropland_high_with_manure_category(
    *,
    has_animal_manure_used: bool,
    has_bare_fallow: bool,
    has_low_residue_producing_crops: bool,
    has_n_fixing_crop_or_inorganic_n_fertiliser_used: bool,
    has_residue_removed_or_burnt: bool,
    **_
) -> Union[int, None]:
    """
    Checks the Cropland High with Manure IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.

    Returns
    -------
    int | none
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            has_animal_manure_used
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_high_without_manure_category(
    *,
    has_animal_manure_used: bool,
    has_bare_fallow: bool,
    has_cover_crop: bool,
    has_irrigation: bool,
    has_low_residue_producing_crops: bool,
    has_n_fixing_crop_or_inorganic_n_fertiliser_used: bool,
    has_organic_fertiliser_or_soil_amendment_used: bool,
    has_practice_increasing_c_input: bool,
    has_residue_removed_or_burnt: bool,
    **_
) -> Union[int, None]:
    """
    Checks the Cropland High without Manure IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_cover_crop : bool
        Indicates whether cover crops are present on more than 30% of the site.
    has_irrigation : bool
        Indicates whether irrigation is applied to more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_organic_fertiliser_or_soil_amendment_used : bool
        Indicates whether organic fertiliser or soil amendments are used on more than 30% of the site.
    has_practice_increasing_c_input : bool
        Indicates whether practices increasing carbon input are present on more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            any([
                has_irrigation,
                has_practice_increasing_c_input,
                has_cover_crop,
                has_organic_fertiliser_or_soil_amendment_used
            ]),
            not has_animal_manure_used
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_medium_category(
    *,
    has_animal_manure_used: bool,
    has_bare_fallow: bool,
    has_cover_crop: bool,
    has_irrigation: bool,
    has_low_residue_producing_crops: bool,
    has_n_fixing_crop_or_inorganic_n_fertiliser_used: bool,
    has_organic_fertiliser_or_soil_amendment_used: bool,
    has_practice_increasing_c_input: bool,
    has_residue_removed_or_burnt: bool,
    **_
) -> Union[int, None]:
    """
    Checks the Cropland Medium IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_cover_crop : bool
        Indicates whether cover crops are present on more than 30% of the site.
    has_irrigation : bool
        Indicates whether irrigation is applied to more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_organic_fertiliser_or_soil_amendment_used : bool
        Indicates whether organic fertiliser or soil amendments are used on more than 30% of the site.
    has_practice_increasing_c_input : bool
        Indicates whether practices increasing carbon input are present on more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            has_residue_removed_or_burnt,
            has_animal_manure_used
        ]),
        2: all([
            not has_residue_removed_or_burnt,
            any([
                has_low_residue_producing_crops,
                has_bare_fallow
            ]),
            any([
                has_irrigation,
                has_practice_increasing_c_input,
                has_cover_crop,
                has_organic_fertiliser_or_soil_amendment_used,
            ])
        ]),
        3: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            not has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            any([
                has_irrigation,
                has_practice_increasing_c_input,
                has_cover_crop,
                has_organic_fertiliser_or_soil_amendment_used
            ])
        ]),
        4: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            not has_irrigation,
            not has_organic_fertiliser_or_soil_amendment_used,
            not has_practice_increasing_c_input,
            not has_cover_crop
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_low_category(
    *,
    has_animal_manure_used: bool,
    has_bare_fallow: bool,
    has_cover_crop: bool,
    has_irrigation: bool,
    has_low_residue_producing_crops: bool,
    has_n_fixing_crop_or_inorganic_n_fertiliser_used: bool,
    has_organic_fertiliser_or_soil_amendment_used: bool,
    has_practice_increasing_c_input: bool,
    has_residue_removed_or_burnt: bool,
    **_
) -> Union[int, None]:
    """
    Checks the Cropland Low IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_cover_crop : bool
        Indicates whether cover crops are present on more than 30% of the site.
    has_irrigation : bool
        Indicates whether irrigation is applied to more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_organic_fertiliser_or_soil_amendment_used : bool
        Indicates whether organic fertiliser or soil amendments are used on more than 30% of the site.
    has_practice_increasing_c_input : bool
        Indicates whether practices increasing carbon input are present on more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            has_residue_removed_or_burnt,
            not has_animal_manure_used
        ]),
        2: all([
            not has_residue_removed_or_burnt,
            any([
                has_low_residue_producing_crops,
                has_bare_fallow
            ]),
            not has_irrigation,
            not has_practice_increasing_c_input,
            not has_cover_crop,
            not has_organic_fertiliser_or_soil_amendment_used
        ]),
        3: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            not has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            not has_irrigation,
            not has_organic_fertiliser_or_soil_amendment_used,
            not has_practice_increasing_c_input,
            not has_cover_crop
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


_CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE = {
    IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE: _check_cropland_high_with_manure_category,
    IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE: _check_cropland_high_without_manure_category,
    IpccCarbonInputCategory.CROPLAND_MEDIUM: _check_cropland_medium_category,
    IpccCarbonInputCategory.CROPLAND_LOW: _check_cropland_low_category
}
"""
A decision tree for assigning IPCC Carbon Input Categories to Cropland based on specific conditions.

Key: IpccCarbonInputCategory
Value: Corresponding function to check if the given conditions are met for the category.
"""

_DECISION_TREE_FROM_IPCC_MANAGEMENT_CATEGORY = {
    IpccManagementCategory.IMPROVED_GRASSLAND: _GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.FULL_TILLAGE: _CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.REDUCED_TILLAGE: _CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.NO_TILLAGE: _CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE
}
"""
A decision tree mapping IPCC Management Categories to respective Carbon Input Category decision trees.

Key: IpccManagementCategory
Value: Decision tree for Carbon Input Categories corresponding to the management category.
"""

_DEFAULT_CARBON_INPUT_CATEGORY = {
    IpccManagementCategory.IMPROVED_GRASSLAND: IpccCarbonInputCategory.UNKNOWN,
    IpccManagementCategory.FULL_TILLAGE: IpccCarbonInputCategory.UNKNOWN,
    IpccManagementCategory.REDUCED_TILLAGE: IpccCarbonInputCategory.UNKNOWN,
    IpccManagementCategory.NO_TILLAGE: IpccCarbonInputCategory.UNKNOWN
}
"""
A mapping from IPCC Management Categories to default Carbon Input Categories.

Key: IpccManagementCategory
Value: Default Carbon Input Category for the corresponding Management Category.
"""


def _get_carbon_input_kwargs(
    management_nodes: list[dict]
) -> dict:
    """
    Creates CarbonInputArgs based on the provided list of management nodes.

    Parameters
    ----------
    management_nodes : list[dict]
        The list of management nodes.

    Returns
    -------
    dict
        The carbon input keyword arguments.
    """

    PRACTICE_INCREASING_C_INPUT_LOOKUP = LOOKUPS["landUseManagement"]
    LOW_RESIDUE_PRODUCING_CROP_LOOKUP = LOOKUPS["landCover"][1]
    N_FIXING_CROP_LOOKUP = LOOKUPS["landCover"][2]

    # To prevent double counting already explicitly checked practices.
    EXCLUDED_PRACTICE_TERM_IDS = {
        _IMPROVED_PASTURE_TERM_ID,
        _ANIMAL_MANURE_USED_TERM_ID,
        _INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID,
        _ORGANIC_FERTILISER_USED_TERM_ID
    }

    crop_residue_management_nodes = filter_list_term_type(management_nodes, [TermTermType.CROPRESIDUEMANAGEMENT])
    land_cover_nodes = filter_list_term_type(management_nodes, [TermTermType.LANDCOVER])
    land_use_management_nodes = filter_list_term_type(management_nodes, [TermTermType.LANDUSEMANAGEMENT])
    system_nodes = filter_list_term_type(management_nodes, [TermTermType.SYSTEM])
    water_regime_nodes = filter_list_term_type(management_nodes, [TermTermType.WATERREGIME])

    has_animal_manure_used = any(
        get_node_value(node) for node in land_use_management_nodes if node_term_match(node, _ANIMAL_MANURE_USED_TERM_ID)
    )

    has_bare_fallow = cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=_SHORT_BARE_FALLOW_TERM_ID,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    has_cover_crop = cumulative_nodes_match(
        is_cover_crop,
        land_cover_nodes,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    has_inorganic_n_fertiliser_used = any(
        get_node_value(node) for node in land_use_management_nodes
        if node_term_match(node, _INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID)
    )

    has_irrigation = check_irrigation(water_regime_nodes)

    has_low_residue_producing_crops = cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=LOW_RESIDUE_PRODUCING_CROP_LOOKUP,
        target_lookup_values=True,
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD  # Requires a supermajority (>70%).
    )

    has_n_fixing_crop = cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=N_FIXING_CROP_LOOKUP,
        target_lookup_values=True,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    has_n_fixing_crop_or_inorganic_n_fertiliser_used = has_n_fixing_crop or has_inorganic_n_fertiliser_used

    has_organic_fertiliser_or_soil_amendment_used = any(
        get_node_value(node) for node in land_use_management_nodes
        if node_term_match(node, [_ORGANIC_FERTILISER_USED_TERM_ID, _SOIL_AMENDMENT_USED_TERM_ID])
    )

    has_practice_increasing_c_input = cumulative_nodes_match(
        lambda node: (
            node_lookup_match(node, PRACTICE_INCREASING_C_INPUT_LOOKUP, True)
            and not node_term_match(node, EXCLUDED_PRACTICE_TERM_IDS)
        ),
        land_use_management_nodes + system_nodes,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    has_residue_removed_or_burnt = cumulative_nodes_term_match(
        crop_residue_management_nodes,
        target_term_ids=get_residue_removed_or_burnt_terms(),
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    num_grassland_improvements = [
        has_irrigation,
        has_practice_increasing_c_input,
        has_n_fixing_crop_or_inorganic_n_fertiliser_used,
        has_organic_fertiliser_or_soil_amendment_used
    ].count(True)

    return {
        "has_animal_manure_used": has_animal_manure_used,
        "has_bare_fallow": has_bare_fallow,
        "has_cover_crop": has_cover_crop,
        "has_irrigation": has_irrigation,
        "has_low_residue_producing_crops": has_low_residue_producing_crops,
        "has_n_fixing_crop_or_inorganic_n_fertiliser_used": has_n_fixing_crop_or_inorganic_n_fertiliser_used,
        "has_organic_fertiliser_or_soil_amendment_used": has_organic_fertiliser_or_soil_amendment_used,
        "has_practice_increasing_c_input": has_practice_increasing_c_input,
        "has_residue_removed_or_burnt": has_residue_removed_or_burnt,
        "num_grassland_improvements": num_grassland_improvements
    }


def _should_run_inventory_year(group: dict) -> bool:
    """
    Determines whether there is sufficient data in an inventory year to run the tier 1 model.

    1. Check if all required keys are present.
    2. Check if the land use category is not "OTHER" or "UNKNOWN"
    3. Check if the management category is not "UNKNOWN"
    4. Check if the carbon input category is not "UNKNOWN"

    Parameters
    ----------
    group : dict
        Dictionary containing information for a specific inventory year.

    Returns
    -------
    bool
        True if the inventory year is valid, False otherwise.
    """
    return all(key in group.keys() for key in _REQUIRED_KEYS) and all([
        group.get(_InventoryKey.LU_CATEGORY) not in [IpccLandUseCategory.OTHER, IpccLandUseCategory.UNKNOWN],
        group.get(_InventoryKey.MG_CATEGORY) not in [IpccManagementCategory.UNKNOWN],
        group.get(_InventoryKey.CI_CATEGORY) not in [IpccCarbonInputCategory.UNKNOWN]
    ])
