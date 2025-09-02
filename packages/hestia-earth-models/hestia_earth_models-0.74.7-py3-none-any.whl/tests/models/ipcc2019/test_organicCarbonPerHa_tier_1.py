from itertools import product
import json
from numpy import array
from numpy.testing import assert_array_almost_equal
from pytest import mark
from unittest.mock import MagicMock, patch

from hestia_earth.models.utils.ecoClimateZone import EcoClimateZone
from hestia_earth.models.ipcc2019.organicCarbonPerHa import MODEL, TERM_ID
from hestia_earth.models.ipcc2019.organicCarbonPerHa_utils import (
    IpccCarbonInputCategory, IpccLandUseCategory, IpccManagementCategory, IpccSoilCategory, sample_constant,
    sample_plus_minus_error, sample_plus_minus_uncertainty
)
from hestia_earth.models.ipcc2019.organicCarbonPerHa_tier_1 import (
    _assign_ipcc_carbon_input_category, _assign_ipcc_land_use_category, _assign_ipcc_management_category,
    _assign_ipcc_soil_category, _calc_missing_equilibrium_years, _calc_regime_start_years, _calc_soc_stocks,
    _check_cropland_low_category, _check_cropland_medium_category, _get_carbon_input_kwargs, _get_sample_func,
    _get_soc_ref_preview, _InventoryKey, _sample_parameter, _EXCLUDED_ECO_CLIMATE_ZONES
)

from tests.utils import fixtures_path

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}_tier_1"
utils_path = f"hestia_earth.models.{MODEL}.{TERM_ID}_utils"
term_path = "hestia_earth.models.utils.term"
property_path = "hestia_earth.models.utils.property"

fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

ITERATIONS = 1000

COVER_CROP_PROPERTY_TERM_IDS = [
    "catchCrop",
    "coverCrop",
    "groundCover",
    "longFallowCrop",
    "shortFallowCrop"
]

IRRIGATED_TERM_IDS = [
    "rainfedDeepWater",
    "rainfedDeepWaterWaterDepth100Cm",
    "rainfedDeepWaterWaterDepth50100Cm",
    "irrigatedTypeUnspecified",
    "irrigatedCenterPivotIrrigation",
    "irrigatedContinuouslyFlooded",
    "irrigatedDripIrrigation",
    "irrigatedFurrowIrrigation",
    "irrigatedLateralMoveIrrigation",
    "irrigatedLocalizedIrrigation",
    "irrigatedManualIrrigation",
    "irrigatedSurfaceIrrigationMultipleDrainagePeriods",
    "irrigatedSurfaceIrrigationSingleDrainagePeriod",
    "irrigatedSprinklerIrrigation",
    "irrigatedSubIrrigation",
    "irrigatedSurfaceIrrigationDrainageRegimeUnspecified"
]

RESIDUE_REMOVED_OR_BURNT_TERM_IDS = [
    "residueBurnt",
    "residueRemoved"
]

UPLAND_RICE_LAND_COVER_TERM_IDS = [
    "ricePlantUpland"
]


# kwargs, sample_func, expected_shape
PARAMS_GET_SAMPLE_FUNC = [
    ({"value": 1}, sample_constant),
    ({"value": 1, "error": 10}, sample_plus_minus_error),
    ({"value": 1, "uncertainty": 10}, sample_plus_minus_uncertainty)
]
IDS_GET_SAMPLE_FUNC = ["constant", "+/- error", "+/- uncertainty"]


@mark.parametrize("kwargs, sample_func", PARAMS_GET_SAMPLE_FUNC, ids=IDS_GET_SAMPLE_FUNC)
def test_get_sample_func(kwargs, sample_func):
    result = _get_sample_func(kwargs)
    assert result == sample_func


SOC_REF_PARAMS = [p for p in product(IpccSoilCategory, EcoClimateZone) if _get_soc_ref_preview(*p)]
FACTOR_PARAMS = list(product(
    [c for c in IpccLandUseCategory] + [c for c in IpccManagementCategory] + [c for c in IpccCarbonInputCategory],
    [e for e in EcoClimateZone if e not in _EXCLUDED_ECO_CLIMATE_ZONES]
))

# ipcc_category, eco_climate_zone
PARAMS_SAMPLE_PARAMETER = SOC_REF_PARAMS + FACTOR_PARAMS
IDS_SAMPLE_PARAMETER = [f"{p[0]} + {p[1].name}" for p in PARAMS_SAMPLE_PARAMETER]


@mark.parametrize("ipcc_category, eco_climate_zone", PARAMS_SAMPLE_PARAMETER, ids=IDS_SAMPLE_PARAMETER)
def test_sample_parameter(ipcc_category, eco_climate_zone):
    """
    Check that every combination of parameter and eco_climate_zone can be sampled without raising an error.
    """
    EXPECTED_SHAPE = (1, ITERATIONS)
    result = _sample_parameter(ITERATIONS, ipcc_category, eco_climate_zone)
    assert result.shape == EXPECTED_SHAPE


# subfolder, expected
SOIL_CATEGORY_PARAMS = [
    ("fractional", IpccSoilCategory.WETLAND_SOILS),
    ("no-measurements", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS),
    ("sandy-override", IpccSoilCategory.SANDY_SOILS),
    ("soilType/hac", IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS),
    ("soilType/lac", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS),
    ("soilType/org", IpccSoilCategory.ORGANIC_SOILS),
    ("soilType/pod", IpccSoilCategory.SPODIC_SOILS),
    ("soilType/san", IpccSoilCategory.SANDY_SOILS),
    ("soilType/vol", IpccSoilCategory.VOLCANIC_SOILS),
    ("soilType/wet", IpccSoilCategory.WETLAND_SOILS),
    ("usdaSoilType/hac", IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS),
    ("usdaSoilType/lac", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS),
    ("usdaSoilType/org", IpccSoilCategory.ORGANIC_SOILS),
    ("usdaSoilType/pod", IpccSoilCategory.SPODIC_SOILS),
    ("usdaSoilType/san", IpccSoilCategory.SANDY_SOILS),
    ("usdaSoilType/vol", IpccSoilCategory.VOLCANIC_SOILS),
    ("usdaSoilType/wet", IpccSoilCategory.WETLAND_SOILS),
    ("with-depths", IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS)  # Closes #1248
]


@mark.parametrize(
    "subfolder, expected",
    SOIL_CATEGORY_PARAMS,
    ids=[params[0] for params in SOIL_CATEGORY_PARAMS]
)
def test_assign_ipcc_soil_category(subfolder: str, expected: IpccSoilCategory):
    folder = f"{fixtures_folder}/IpccSoilCategory/{subfolder}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _assign_ipcc_soil_category(site.get("measurements", []))
    assert result == expected


# subfolder, soil_category, expected
LAND_USE_CATEGORY_PARAMS = [
    ("annual-crops", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.ANNUAL_CROPS),
    ("annual-crops-wet", IpccSoilCategory.WETLAND_SOILS, IpccLandUseCategory.ANNUAL_CROPS_WET),
    ("forest", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.FOREST),
    ("fractional", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.PERENNIAL_CROPS),
    ("grassland", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.GRASSLAND),
    ("irrigated-upland-rice", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.PADDY_RICE_CULTIVATION),
    ("native", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.NATIVE),
    ("other", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.OTHER),
    ("paddy-rice-cultivation", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.PADDY_RICE_CULTIVATION),
    ("perennial-crops", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.PERENNIAL_CROPS),
    ("set-aside", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.SET_ASIDE),
    ("set-aside-override", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.SET_ASIDE),
    ("upland-rice", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.ANNUAL_CROPS),
    ("unknown", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.UNKNOWN)
]


@mark.parametrize(
    "subfolder, soil_category, expected",
    LAND_USE_CATEGORY_PARAMS,
    ids=[params[0] for params in LAND_USE_CATEGORY_PARAMS]
)
@patch(f"{class_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{utils_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_assign_ipcc_land_use_category(
    search_mock: MagicMock,
    _get_cover_crop_property_terms_mock: MagicMock,
    _get_irrigated_terms_mock: MagicMock,
    _get_upland_rice_land_cover_terms_mock: MagicMock,
    subfolder: str,
    soil_category: IpccSoilCategory,
    expected: IpccLandUseCategory
):
    folder = f"{fixtures_folder}/IpccLandUseCategory/{subfolder}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _assign_ipcc_land_use_category(site.get("management", []), soil_category)
    assert result == expected

    search_mock.assert_not_called()  # Ensure that the term utils are properly mocked.


# subfolder, land_use_category, expected
MANAGEMENT_CATEGORY_PARAMS = [
    ("fractional-annual-crops", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.REDUCED_TILLAGE),
    ("fractional-annual-crops-wet", IpccLandUseCategory.ANNUAL_CROPS_WET, IpccManagementCategory.REDUCED_TILLAGE),
    ("fractional-grassland", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.IMPROVED_GRASSLAND),
    ("full-tillage", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.FULL_TILLAGE),
    ("high-intensity-grazing", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.HIGH_INTENSITY_GRAZING),
    ("improved-grassland", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.IMPROVED_GRASSLAND),
    ("no-tillage", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.NO_TILLAGE),
    ("nominally-managed/native-pasture", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.NOMINALLY_MANAGED),
    (
        "nominally-managed/nominally-managed-pasture",
        IpccLandUseCategory.GRASSLAND,
        IpccManagementCategory.NOMINALLY_MANAGED
    ),
    ("not-relevant", IpccLandUseCategory.OTHER, IpccManagementCategory.NOT_RELEVANT),
    ("reduced-tillage", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.REDUCED_TILLAGE),
    ("severely-degraded", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.SEVERELY_DEGRADED),
    ("unknown/annual-crops", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.UNKNOWN),
    ("unknown/annual-crops-wet", IpccLandUseCategory.ANNUAL_CROPS_WET, IpccManagementCategory.UNKNOWN),
    ("unknown/grassland", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.UNKNOWN)
]


@mark.parametrize(
    "subfolder, land_use_category, expected",
    MANAGEMENT_CATEGORY_PARAMS,
    ids=[params[0] for params in MANAGEMENT_CATEGORY_PARAMS]
)
def test_assign_ipcc_management_category(
    subfolder: str, land_use_category: IpccLandUseCategory, expected: IpccManagementCategory
):
    folder = f"{fixtures_folder}/IpccManagementCategory/{subfolder}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _assign_ipcc_management_category(site.get("management", []), land_use_category)
    assert result == expected


@mark.parametrize("key", [1, 2, 3, 4], ids=lambda key: f"scenario-{key}")
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{utils_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_check_cropland_medium_category(
    search_mock: MagicMock,
    _get_cover_crop_property_terms_mock: MagicMock,
    _get_irrigated_terms_mock: MagicMock,
    _get_residue_removed_or_burnt_terms_mock: MagicMock,
    key: int
):
    """
    Tests each set of cropland medium conditions against a list of nodes that such satisfy it. The function returns the
    key of the matching condition set, which should match the suffix of the fixtures subfolder.
    """
    folder = f"{fixtures_folder}/IpccCarbonInputCategory/cropland-medium/scenario-{key}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _check_cropland_medium_category(**_get_carbon_input_kwargs(site.get("management", [])))
    assert result == key

    search_mock.assert_not_called()  # Ensure that the term utils are properly mocked.


@mark.parametrize("key", [1, 2, 3], ids=lambda key: f"scenario-{key}")
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{utils_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_check_cropland_low_category(
    search_mock: MagicMock,
    _get_cover_crop_property_terms_mock: MagicMock,
    _get_irrigated_terms_mock: MagicMock,
    _get_residue_removed_or_burnt_terms_mock: MagicMock,
    key: int
):
    """
    Tests each set of cropland low conditions against a list of nodes that such satisfy it. The function returns the
    key of the matching condition set, which should match the suffix of the fixtures subfolder.
    """
    folder = f"{fixtures_folder}/IpccCarbonInputCategory/cropland-low/scenario-{key}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _check_cropland_low_category(**_get_carbon_input_kwargs(site.get("management", [])))
    assert result == key

    search_mock.assert_not_called()  # Ensure that the term utils are properly mocked.


# subfolder, management_category, expected
CARBON_INPUT_CATEGORY_PARAMS = [
    (
        "cropland-high-with-manure",
        IpccManagementCategory.FULL_TILLAGE,
        IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE
    ),
    (
        "cropland-high-without-manure/organic-fertiliser",  # Closes issue 743
        IpccManagementCategory.FULL_TILLAGE,
        IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE
    ),
    (
        "cropland-high-without-manure/soil-amendment",  # Closes issue 743
        IpccManagementCategory.FULL_TILLAGE,
        IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE
    ),
    ("cropland-low/scenario-1", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_LOW),
    ("cropland-low/scenario-2", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_LOW),
    ("cropland-low/scenario-3", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_LOW),
    ("cropland-medium/scenario-1", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_MEDIUM),
    ("cropland-medium/scenario-2", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_MEDIUM),
    ("cropland-medium/scenario-3", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_MEDIUM),
    ("cropland-medium/scenario-4", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_MEDIUM),
    ("grassland-high", IpccManagementCategory.IMPROVED_GRASSLAND, IpccCarbonInputCategory.GRASSLAND_HIGH),
    (
        "grassland-medium/0-improvements",
        IpccManagementCategory.IMPROVED_GRASSLAND,
        IpccCarbonInputCategory.GRASSLAND_MEDIUM
    ),
    (
        "grassland-medium/1-improvements",
        IpccManagementCategory.IMPROVED_GRASSLAND,
        IpccCarbonInputCategory.GRASSLAND_MEDIUM
    ),
    ("not-relevant", IpccManagementCategory.NOT_RELEVANT, IpccCarbonInputCategory.NOT_RELEVANT),
    ("unknown/cropland", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.UNKNOWN),
    ("unknown/grassland", IpccManagementCategory.IMPROVED_GRASSLAND, IpccCarbonInputCategory.UNKNOWN)
]


@mark.parametrize(
    "subfolder, management_category, expected",
    CARBON_INPUT_CATEGORY_PARAMS,
    ids=[params[0] for params in CARBON_INPUT_CATEGORY_PARAMS]
)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{utils_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_assign_ipcc_carbon_input_category(
    search_mock: MagicMock,
    _get_cover_crop_property_terms_mock: MagicMock,
    _get_irrigated_terms_mock: MagicMock,
    _get_residue_removed_or_burnt_terms_mock: MagicMock,
    subfolder: str,
    management_category: IpccManagementCategory,
    expected: IpccCarbonInputCategory
):
    folder = f"{fixtures_folder}/IpccCarbonInputCategory/{subfolder}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _assign_ipcc_carbon_input_category(site.get("management", []), management_category)
    assert result == expected

    search_mock.assert_not_called()  # Ensure that the term utils are properly mocked.


TIMESTAMPS_CALC_SOC_STOCK = [1990, 1995, 2000, 2005, 2010, 2015, 2020]

# regime_start_years, soc_equilibriums, expected
PARAMS_CALC_SOC_STOCK = [
    (
        [1970, 1995, 1995, 1995, 1995, 1995, 1995],
        array([[77.000], [70.840], [70.840], [70.840], [70.840], [70.840], [70.840]]),
        array([[77.000], [75.460], [73.920], [72.380], [70.840], [70.840], [70.840]])
    ),
    (
        [1970, 1995, 1995, 1995, 2010, 2010, 2010],
        array([[77.000], [70.840], [70.840], [70.840], [80.850], [80.850], [80.850]]),
        array([[77.000], [75.460], [73.920], [72.380], [74.498], [76.615], [78.733]])
    ),
    (
        [1970, 1995, 1995, 1995, 1995, 2015, 2015],
        array([[80.850], [70.840], [70.840], [70.840], [70.840], [80.850], [80.850]]),
        array([[80.850], [78.348], [75.845], [73.343], [70.840], [73.343], [75.845]])
    ),
    (
        [1970, 1970, 2000, 2000, 2000, 2000, 2000],
        array([[80.850], [80.850], [77.000], [77.000], [77.000], [77.000], [77.000]]),
        array([[80.850], [80.850], [79.888], [78.925], [77.963], [77.000], [77.000]])
    ),
    (
        [1970, 1970, 1970, 1970, 2010, 2010, 2010],
        array([[70.840], [70.840], [70.840], [70.840], [80.850], [80.850], [80.850]]),
        array([[70.840], [70.840], [70.840], [70.840], [73.343], [75.845], [78.348]])
    ),
    (
        [1970, 1970, 2000, 2000, 2000, 2015, 2020],
        array([[70.840], [70.840], [80.850], [80.850], [80.850], [70.840], [80.850]]),
        array([[70.840], [70.840], [73.343], [75.845], [78.348], [76.471], [77.565]])
    )
]
IDS_CALC_SOC_STOCK = [f"land-unit-{i+1}" for i in range(len(PARAMS_CALC_SOC_STOCK))]


@mark.parametrize("regime_start_years, soc_equilibriums, expected", PARAMS_CALC_SOC_STOCK, ids=IDS_CALC_SOC_STOCK)
def test_calc_soc_stocks(regime_start_years, soc_equilibriums, expected):
    """
    Test the interpolation between SOC equilibriums using test data provided in IPCC (2019).
    """
    result = _calc_soc_stocks(
        TIMESTAMPS_CALC_SOC_STOCK, regime_start_years, soc_equilibriums
    )
    assert_array_almost_equal(result, expected, decimal=3)


TEST_INVENTORY = {
        1960: {
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory.FOREST,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory.NOT_RELEVANT,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.NOT_RELEVANT
        },
        1965: {
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory.FOREST,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory.NOT_RELEVANT,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.NOT_RELEVANT
        },
        1970: {
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory.GRASSLAND,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory.NOMINALLY_MANAGED,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.NOT_RELEVANT
        },
        1995: {
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory.ANNUAL_CROPS,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory.FULL_TILLAGE,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.CROPLAND_LOW
        },
        2003: {
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory.ANNUAL_CROPS,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory.FULL_TILLAGE,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.CROPLAND_MEDIUM
        },
        2025: {
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory.ANNUAL_CROPS,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory.FULL_TILLAGE,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.CROPLAND_MEDIUM
        },
        2026: {
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory.ANNUAL_CROPS,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory.REDUCED_TILLAGE,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.CROPLAND_MEDIUM
        }
    }

EXPECTED_MISSING_YEARS = {
    1990: {
        _InventoryKey.LU_CATEGORY: IpccLandUseCategory.GRASSLAND,
        _InventoryKey.MG_CATEGORY: IpccManagementCategory.NOMINALLY_MANAGED,
        _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.NOT_RELEVANT
    },
    2023: {
        _InventoryKey.LU_CATEGORY: IpccLandUseCategory.ANNUAL_CROPS,
        _InventoryKey.MG_CATEGORY: IpccManagementCategory.FULL_TILLAGE,
        _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory.CROPLAND_MEDIUM
    }
}


def test_calc_missing_equilibrium_years():
    result = _calc_missing_equilibrium_years(TEST_INVENTORY)
    assert result == EXPECTED_MISSING_YEARS


def test_calc_regime_start_years():
    EXPECTED = [1940, 1940, 1970, 1995, 2003, 2003, 2026]
    result = _calc_regime_start_years(TEST_INVENTORY)
    assert result == EXPECTED
