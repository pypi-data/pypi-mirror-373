from functools import reduce
import json
from pytest import mark
from os.path import isfile
from unittest.mock import MagicMock, patch

from tests.utils import fake_new_emission, fixtures_path, order_list

from hestia_earth.models.ipcc2019.nonCo2EmissionsToAirNaturalVegetationBurning import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.nonCo2EmissionsToAirNaturalVegetationBurning"
fixtures_folder = f"{fixtures_path}/{MODEL}/nonCo2EmissionsToAirNaturalVegetationBurning"
biomass_utils_path = f"hestia_earth.models.{MODEL}.biomass_utils"

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


RUN_SCENARIOS = [
    ("forest-to-cropland", 4),
    ("historical-land-cover-mix", 3),
    ("deforestation-reforestation", 1),  # gains should not offset losses
    ("no-clearance-via-fire", 1),  # LUC in the UK, which has a percentage burned factor of 0, should run
    ("forest-to-cropland-with-ground-cover", 4),  # Cover crops/ground covers should be ignored
    ("single-year", 1)  # should not run, multiple years of land cover data required
]


RUN_PARAMS = reduce(
    lambda params, scenario: params + [(scenario[0], scenario[1], i) for i in range(scenario[1])],
    RUN_SCENARIOS,
    list()
)
"""List of (subfolder: str, num_cycles: int, cycle_index: int)."""

RUN_IDS = [f"{param[0]}, cycle{param[2]}" for param in RUN_PARAMS]


@mark.parametrize("subfolder, num_cycles, cycle_index", RUN_PARAMS, ids=RUN_IDS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
@patch(f"{biomass_utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.related_cycles")
@patch(f"{class_path}._get_site")
def test_run(
    get_site_mock: MagicMock,
    related_cycles_mock: MagicMock,
    _get_cover_crop_property_terms_mock: MagicMock,
    _new_emission_mock: MagicMock,
    subfolder: str,
    num_cycles: int,
    cycle_index: int
):
    """
    Test `run` function for each cycle in each scenario.
    """
    site = _load_fixture(f"{fixtures_folder}/{subfolder}/site.jsonld")
    cycle = _load_fixture(f"{fixtures_folder}/{subfolder}/cycle{cycle_index}.jsonld")
    expected = _load_fixture(f"{fixtures_folder}/{subfolder}/result{cycle_index}.jsonld", default=[])

    cycles = [_load_fixture(f"{fixtures_folder}/{subfolder}/cycle{i}.jsonld") for i in range(num_cycles)]

    get_site_mock.return_value = site
    related_cycles_mock.return_value = cycles

    result = run(cycle)
    assert order_list(result) == order_list(expected)


@patch(f"{biomass_utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
def test_should_run_no_data(*args):
    CYCLE = {}
    EXPECTED = False

    result, *_ = _should_run(CYCLE)
    assert result == EXPECTED


@patch(f"{biomass_utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_no_data(*args):
    CYCLE = {}
    EXPECTED = []

    result = run(CYCLE)
    assert result == EXPECTED
