import json
from numpy.typing import NDArray
from os.path import isfile
from pytest import mark
from unittest.mock import MagicMock, patch

from hestia_earth.models.ipcc2019.organicCarbonPerHa import _should_run, MODEL, run, TERM_ID
from hestia_earth.models.ipcc2019.organicCarbonPerHa_utils import sample_constant

from tests.utils import fake_new_measurement, fixtures_path

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
tier_1_utils_path = f"hestia_earth.models.{MODEL}.{TERM_ID}_tier_1"
tier_2_utils_path = f"hestia_earth.models.{MODEL}.{TERM_ID}_tier_2"
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

UPLAND_RICE_CROP_TERM_IDS = [
    "riceGrainInHuskUpland"
]

UPLAND_RICE_LAND_COVER_TERM_IDS = [
    "ricePlantUpland"
]

DEFAULT_PROPERTIES = {
    "manureDryKgMass": {
        "carbonContent": {
            "value": 38.4
        },
        "nitrogenContent": {
            "value": 2.65
        },
        "ligninContent": {
            "value": 9.67
        },
        "dryMatter": {
            "value": 100
        }
    },
    "cattleSolidManureDryKgMass": {
        "carbonContent": {
            "value": 46.4
        },
        "nitrogenContent": {
            "value": 2.65
        },
        "ligninContent": {
            "value": 11
        },
        "dryMatter": {
            "value": 100
        }
    },
    "cattleSolidManureFreshKgMass": {
        "carbonContent": {
            "value": 9.27
        },
        "nitrogenContent": {
            "value": 0.53
        },
        "ligninContent": {
            "value": 2.2
        },
        "dryMatter": {
            "value": 20
        }
    },
    "cattleLiquidManureKgMass": {
        "carbonContent": {
            "value": 4.3
        },
        "nitrogenContent": {
            "value": 0.245
        },
        "ligninContent": {
            "value": 1.02
        },
        "dryMatter": {
            "value": 9.18
        }
    },
    "cattleSolidManureDryKgN": {
        "carbonContent": {
            "value": 1750
        },
        "nitrogenContent": {
            "value": 100
        },
        "ligninContent": {
            "value": 415
        },
        "dryMatter": {
            "value": 3773.585
        }
    },
    "cattleSolidManureFreshKgN": {
        "carbonContent": {
            "value": 1750
        },
        "nitrogenContent": {
            "value": 100
        },
        "ligninContent": {
            "value": 415
        },
        "dryMatter": {
            "value": 3775.611
        }
    },
    "cattleLiquidManureKgN": {
        "carbonContent": {
            "value": 1750
        },
        "nitrogenContent": {
            "value": 100
        },
        "ligninContent": {
            "value": 415
        },
        "dryMatter": {
            "value": 3738.968
        }
    }
}


def fake_calc_descriptive_stats(arr: NDArray, *_args, **_kwargs):
    return {"value": [round(row[0], 6) for row in arr]}


def fake_find_term_property(term: dict, property: str, *_):
    term_id = term.get('@id', None)
    return DEFAULT_PROPERTIES.get(term_id, {}).get(property, {})


def order_list(values: list[dict]) -> list[dict]:
    return sorted(values, key=lambda node: (
        node.get("term", {}).get('@id', ""),   # sort by `term.@id`
        node.get("methodClassification", ""),  # then by `methodClassifaction`
        node.get("dates", [])                  # then by `dates[0]`
    ))


# subfolder, should_run
PARAMS_SHOULD_RUN = [
    ("tier-1-and-2/cropland", True),
    ("tier-1-and-2/with-zero-carbon-input", True),                   # Closes issue 777
    ("tier-1-and-2/with-residues-removed", True),                    # Closes issue #758 and #846
    ("tier-1/cropland-depth-as-float", True),
    ("tier-1/cropland-with-measured-soc", True),
    ("tier-1/cropland-without-measured-soc", True),
    ("tier-1/permanent-pasture", True),
    ("tier-1/should-not-run", False),
    ("tier-1/without-management-with-measured-soc", False),
    ("tier-1/land-use-change", True),                                # Closes issue 755
    ("tier-1/run-with-site-type", False),                            # Closes issue 755
    ("tier-1/cropland-polar", False),                                # Closes issue 794
    ("tier-1/cropland-with-system-increasing-c-input", True),        # Closes issue 851
    ("tier-1/with-gapfilled-start-date-end-date", False),            # Closes issue 972
    ("tier-1/forest-to-orchard-with-ground-cover", True),            # Closes 989
    ("tier-1/forest-to-other-with-ground-cover", True),              # Closes 989
    ("tier-1/land-use-change-with-unknown-management", True),        # Closes issue 1007
    ("tier-2/with-generalised-monthly-measurements", False),         # Closes issue 600
    ("tier-2/with-incomplete-climate-data", False),                  # Closes issue 599
    ("tier-2/with-initial-soc", True),
    ("tier-2/with-multi-year-cycles", True),
    ("tier-2/with-multi-year-cycles-and-missing-properties", True),  # Closes issue 734
    ("tier-2/without-any-measurements", False),                      # Closes issue 594
    ("tier-2/without-initial-soc", True),
    ("tier-2/with-irrigation", True),                                # Closes issue 716
    ("tier-2/with-irrigation-dates", True),                          # Closes issue 716
    ("tier-2/with-paddy-rice", False),                               # Closes issue 718
    ("tier-2/with-sand-without-date", True),                         # Closes issue 739
    ("tier-2/with-irrigated-upland-rice", False),                    # Closes issue 718
    ("tier-2/with-manure-dry-kg-mass", True),                        # Closes issue 763
    ("tier-2/with-manure-fresh-kg-mass", True),                      # Closes issue 763
    ("tier-2/with-manure-liquid-kg-mass", True),                     # Closes issue 763
    ("tier-2/with-manure-dry-kg-n", True),                           # Closes issue 763
    ("tier-2/with-manure-fresh-kg-n", True),                         # Closes issue 763
    ("tier-2/with-manure-liquid-kg-n", True),                        # Closes issue 763
    ("tier-2/with-split-years", True)                                # Closes issue 1177
]
IDS_SHOULD_RUN = [p[0] for p in PARAMS_SHOULD_RUN]


@mark.parametrize("subfolder, should_run", PARAMS_SHOULD_RUN, ids=IDS_SHOULD_RUN)
@patch(f"{tier_2_utils_path}.related_cycles")
@patch(f"{tier_2_utils_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{tier_2_utils_path}.get_upland_rice_crop_terms", return_value=UPLAND_RICE_CROP_TERM_IDS)
@patch(f"{tier_1_utils_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{tier_1_utils_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{utils_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
@patch(f"{property_path}.find_term_property", side_effect=fake_find_term_property)
@patch(f"{property_path}.download_term")
def test_should_run(
    download_term_mock: MagicMock,
    _find_term_property_mock: MagicMock,
    search_mock: MagicMock,
    _get_cover_crop_property_terms_mock: MagicMock,
    _get_irrigated_terms_mock: MagicMock,
    _get_residue_removed_or_burnt_terms_mock: MagicMock,
    _get_upland_rice_land_cover_terms_mock_t1: MagicMock,
    _get_upland_rice_crop_terms_mock: MagicMock,
    _get_upland_rice_land_cover_terms_mock_t2: MagicMock,
    related_cycles_mock: MagicMock,
    subfolder: str,
    should_run: bool
):
    folder = f"{fixtures_folder}/{subfolder}"

    def load_cycles_from_file():
        with open(f"{folder}/cycles.jsonld", encoding='utf-8') as f:
            return json.load(f)

    related_cycles_mock.return_value = (
        load_cycles_from_file() if isfile(f"{folder}/cycles.jsonld") else []
    )

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result, _ = _should_run(site)
    assert result == should_run

    # Ensure that the property and term utils are properly mocked.
    download_term_mock.assert_not_called()
    search_mock.assert_not_called()


@patch(f"{tier_2_utils_path}.related_cycles", return_value=[])
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
@patch(f"{property_path}.download_term")
def test_should_run_no_data(
    download_term_mock: MagicMock,
    search_mock: MagicMock,
    *args
):
    SITE = {}
    EXPECTED = []

    result = run(SITE)

    download_term_mock.assert_not_called()
    search_mock.assert_not_called()
    assert result == EXPECTED


PARAMS_RUN = [subfolder for subfolder, should_run in PARAMS_SHOULD_RUN if should_run]


@mark.parametrize("subfolder", PARAMS_RUN)
@patch(f"{tier_2_utils_path}.related_cycles")
@patch(f"{tier_2_utils_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{tier_2_utils_path}.get_upland_rice_crop_terms", return_value=UPLAND_RICE_CROP_TERM_IDS)
@patch(f"{tier_2_utils_path}.calc_descriptive_stats", side_effect=fake_calc_descriptive_stats)
@patch(f"{tier_2_utils_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{tier_2_utils_path}._get_sample_func", return_value=sample_constant)
@patch(f"{tier_1_utils_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{tier_1_utils_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{tier_1_utils_path}.calc_descriptive_stats", side_effect=fake_calc_descriptive_stats)
@patch(f"{tier_1_utils_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{tier_1_utils_path}._get_sample_func", return_value=sample_constant)
@patch(f"{utils_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
@patch(f"{property_path}.find_term_property", side_effect=fake_find_term_property)
@patch(f"{property_path}.download_term")
def test_run(
    download_term_mock: MagicMock,
    _find_term_property_mock: MagicMock,
    search_mock: MagicMock,
    _get_cover_crop_property_terms_mock: MagicMock,
    _get_irrigated_terms_mock: MagicMock,
    _get_sample_func_mock_t1: MagicMock,
    _new_measurement_mock_t1: MagicMock,
    _calc_descriptive_stats_mock_t1: MagicMock,
    _get_residue_removed_or_burnt_terms_mock: MagicMock,
    _get_upland_rice_land_cover_terms_mock_t1: MagicMock,
    _get_sample_func_mock_t2: MagicMock,
    _new_measurement_mock_t2: MagicMock,
    _mock_calc_descriptive_stats_t2: MagicMock,
    _get_upland_rice_crop_terms_mock: MagicMock,
    _get_upland_rice_land_cover_terms_mock_t2: MagicMock,
    related_cycles_mock: MagicMock,
    subfolder: str
):
    folder = f"{fixtures_folder}/{subfolder}"

    def load_cycles_from_file():
        with open(f"{folder}/cycles.jsonld", encoding='utf-8') as f:
            return json.load(f)

    related_cycles_mock.return_value = (
        load_cycles_from_file() if isfile(f"{folder}/cycles.jsonld") else []
    )

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    with patch(f"{class_path}.ITERATIONS", ITERATIONS):
        result = run(site)

    assert order_list(result) == order_list(expected)

    # Ensure that the property and term utils are properly mocked.
    download_term_mock.assert_not_called()
    search_mock.assert_not_called()


PARAMS_RUN_WITH_STATS = [
    "tier-1-and-2/with-stats",                        # Closes issue 753
    "tier-1-and-2/with-residues-removed-with-stats",  # Closes issue #758 and #846
    "tier-1/cropland-with-stats",                     # Closes issue 753
    "tier-1/land-use-change-with-stats",              # Closes issue 753
    "tier-2/with-stats"                               # Closes issue 753
]


@mark.parametrize("subfolder", PARAMS_RUN_WITH_STATS)
@patch(f"{tier_2_utils_path}.related_cycles")
@patch(f"{tier_2_utils_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{tier_2_utils_path}.get_upland_rice_crop_terms", return_value=UPLAND_RICE_CROP_TERM_IDS)
@patch(f"{tier_2_utils_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{tier_1_utils_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{tier_1_utils_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{tier_1_utils_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{utils_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
@patch(f"{property_path}.find_term_property", side_effect=fake_find_term_property)
@patch(f"{property_path}.download_term")
def test_run_with_stats(
    download_term_mock: MagicMock,
    _find_term_property_mock: MagicMock,
    search_mock: MagicMock,
    _get_cover_crop_property_terms_mock: MagicMock,
    _get_irrigated_terms_mock: MagicMock,
    _new_measurement_mock_t1: MagicMock,
    _get_residue_removed_or_burnt_terms_mock: MagicMock,
    _get_upland_rice_land_cover_terms_mock_t1: MagicMock,
    _new_measurement_mock_t2: MagicMock,
    _get_upland_rice_crop_terms_mock: MagicMock,
    _get_upland_rice_land_cover_terms_mock_t2: MagicMock,
    related_cycles_mock: MagicMock,
    subfolder: str
):
    folder = f"{fixtures_folder}/{subfolder}"

    def load_cycles_from_file():
        with open(f"{folder}/cycles.jsonld", encoding='utf-8') as f:
            return json.load(f)

    related_cycles_mock.return_value = (
        load_cycles_from_file() if isfile(f"{folder}/cycles.jsonld") else []
    )

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    with patch(f"{class_path}.ITERATIONS", ITERATIONS):
        result = run(site)

    assert order_list(result) == order_list(expected)

    # Ensure that the property and term utils are properly mocked.
    download_term_mock.assert_not_called()
    search_mock.assert_not_called()
