import json
from numpy.typing import NDArray
from os.path import isfile
from pytest import mark
from unittest.mock import MagicMock, patch

from hestia_earth.models.ipcc2019.belowGroundBiomass import _build_col_name, _should_run, MODEL, run, TERM_ID
from hestia_earth.models.ipcc2019.biomass_utils import BiomassCategory, sample_constant

from tests.utils import fake_new_measurement, fixtures_path

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
utils_path = f"hestia_earth.models.{MODEL}.biomass_utils"
term_path = "hestia_earth.models.utils.term"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

_ITERATIONS = 1000

COVER_CROP_PROPERTY_TERM_IDS = [
    "catchCrop",
    "coverCrop",
    "groundCover",
    "longFallowCrop",
    "shortFallowCrop"
]


def _load_fixture(path: str, default=None):
    if isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def _fake_calc_descriptive_stats(arr: NDArray, *_args, **_kwargs):
    return {"value": [round(row[0], 6) for row in arr]}


# subfolder, should_run
PARAMS_SHOULD_RUN = [
    ("forest-to-animal-housing", False),
    ("forest-to-cropland", True),
    ("forest-to-cropland-greater-than-100", True),
    ("forest-to-cropland-less-than-100", True),
    ("forest-to-cropland-lcc-q2", True),
    ("forest-to-cropland-lcc-q3", True),
    ("forest-to-cropland-lcc-q4", True),
    ("forest-to-gohac", False),
    ("forest-to-orchard", True),
    ("forest-to-orchard-with-ground-cover", True),                 # Closes 989
    ("forest-to-orchard-with-in-category-lcc", True),
    ("historical-land-cover-mix", True),
    ("historical-argentina-pasture", True),
    ("historical-brazil-maize", True),
    ("perennial-to-grassland-with-pasture-condition", True),
    ("with-gapfilled-start-date-end-date", False),                 # Closes #972
    ("forest-to-cropland-with-missing-equilibrium-year-a", True),  # Closes #1076
    ("forest-to-cropland-with-missing-equilibrium-year-b", True)   # Closes #1076
]
IDS_SHOULD_RUN = [p[0] for p in PARAMS_SHOULD_RUN]


@mark.parametrize("subfolder, should_run", PARAMS_SHOULD_RUN, ids=IDS_SHOULD_RUN)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_should_run(
    search_mock: MagicMock,
    get_cover_crop_property_terms_mock: MagicMock,
    subfolder: str,
    should_run: bool
):
    folder = f"{fixtures_folder}/{subfolder}"

    site = _load_fixture(f"{folder}/site.jsonld", {})

    result, *_ = _should_run(site)
    assert result == should_run

    assert get_cover_crop_property_terms_mock.call_count <= 1  # assert the API call is only requested once
    search_mock.assert_not_called()                            # assert the API call is properly mocked


@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_should_run_no_data(search_mock: MagicMock, get_cover_crop_property_terms_mock: MagicMock):
    SITE = {}
    EXPECTED = False

    result, *_ = _should_run(SITE)
    assert result == EXPECTED

    assert get_cover_crop_property_terms_mock.call_count <= 1  # assert the API call is only requested once
    search_mock.assert_not_called()                            # assert the API call is properly mocked


PARAMS_RUN = [subfolder for subfolder, should_run in PARAMS_SHOULD_RUN if should_run]


@mark.parametrize("subfolder", PARAMS_RUN)
@patch(f"{class_path}.get_source", return_value={})
@patch(f"{class_path}.calc_descriptive_stats", side_effect=_fake_calc_descriptive_stats)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{utils_path}._get_sample_func", return_value=sample_constant)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_run(
    search_mock: MagicMock,
    get_cover_crop_property_terms_mock: MagicMock,
    _get_sample_func_mock: MagicMock,
    _new_measurement_mock: MagicMock,
    _calc_descriptive_stats_mock: MagicMock,
    _mock_source: MagicMock,
    subfolder: str
):
    folder = f"{fixtures_folder}/{subfolder}"

    site = _load_fixture(f"{folder}/site.jsonld", {})
    expected = _load_fixture(f"{folder}/result.jsonld", [])

    with patch(f"{class_path}._ITERATIONS", _ITERATIONS):
        result = run(site)

    assert result == expected

    assert get_cover_crop_property_terms_mock.call_count <= 1  # assert the API call is only requested once
    search_mock.assert_not_called()                            # assert the API call is properly mocked


# subfolder
PARAMS_RUN_WITH_STATS = [
    "forest-to-cropland-with-stats",
    "forest-to-orchard-with-in-category-lcc-with-stats",
    "historical-land-cover-mix-with-stats"
]


@mark.parametrize("subfolder", PARAMS_RUN_WITH_STATS)
@patch(f"{class_path}.get_source", return_value={})
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_run_with_stats(
    search_mock: MagicMock,
    get_cover_crop_property_terms_mock: MagicMock,
    _new_measurement_mock: MagicMock,
    _mock_source: MagicMock,
    subfolder: str
):
    folder = f"{fixtures_folder}/{subfolder}"

    site = _load_fixture(f"{folder}/site.jsonld", {})
    expected = _load_fixture(f"{folder}/result.jsonld", [])

    with patch(f"{class_path}._ITERATIONS", _ITERATIONS):
        result = run(site)

    assert result == expected

    assert get_cover_crop_property_terms_mock.call_count <= 1  # assert the API call is only requested once
    search_mock.assert_not_called()                            # assert the API call is properly mocked


# input, expected
PARAMS_BUILD_COLUMN_NAME = [
    (BiomassCategory.ANNUAL_CROPS, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.COCONUT, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.FOREST, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_FOREST"),
    (BiomassCategory.GRASSLAND, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.JATROPHA, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.JOJOBA, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.NATURAL_FOREST, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_NATURAL_FOREST"),
    (BiomassCategory.OIL_PALM, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.OLIVE, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.ORCHARD, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.OTHER, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.PLANTATION_FOREST, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_PLANTATION_FOREST"),
    (BiomassCategory.RUBBER, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.SHORT_ROTATION_COPPICE, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.TEA, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.VINE, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    (BiomassCategory.WOODY_PERENNIAL, "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"),
    ("Miscellaneous value", "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER")
]
IDS_BUILD_COLUMN_NAME = [p[0] for p in PARAMS_BUILD_COLUMN_NAME]


@mark.parametrize("input, expected", PARAMS_BUILD_COLUMN_NAME, ids=IDS_BUILD_COLUMN_NAME)
def test_build_col_name(input: BiomassCategory, expected: str):
    assert _build_col_name(input) == expected
