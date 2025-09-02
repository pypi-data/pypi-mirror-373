from functools import reduce
import json
from os.path import isfile
from pytest import mark
from unittest.mock import MagicMock, patch

from hestia_earth.models.ipcc2019.co2ToAirBelowGroundBiomassStockChange import MODEL, run

from tests.utils import fake_new_emission, fixtures_path, order_list

class_path = f"hestia_earth.models.{MODEL}.co2ToAirBelowGroundBiomassStockChange"
utils_path = f"hestia_earth.models.{MODEL}.co2ToAirCarbonStockChange_utils"
biomass_utils_path = f"hestia_earth.models.{MODEL}.biomass_utils"
term_path = "hestia_earth.models.utils.term"
fixtures_folder = f"{fixtures_path}/{MODEL}/co2ToAirBelowGroundBiomassStockChange"

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
    ("no-overlapping-cycles", 3),
    ("overlapping-cycles", 4),
    ("complex-overlapping-cycles", 5),
    ("missing-measurement-dates", 3),
    ("no-biomass-measurements", 1),               # Closes #700
    ("non-consecutive-biomass-measurements", 1),  # Closes #827
    ("multiple-method-classifications", 5),       # Closes #764
    ("non-soil-based-gohac-system", 3),           # Closes #848
    ("with-gapfilled-start-date-end-date", 1),    # Closes #972
    ("forest-to-orchard-with-ground-cover", 3),   # Closes #989
    ("orchard-data-complete", 3),                 # Closes #1011
    ("orchard-data-partially-complete", 3),       # Closes #1011
    ("no-measurements-data-complete", 1),         # Closes #1227
    ("no-measurements-data-incomplete", 1)        # Closes #1227
]
"""List of (subfolder: str, num_cycles: int)."""

RUN_PARAMS = reduce(
    lambda params, scenario: params + [(scenario[0], scenario[1], i) for i in range(scenario[1])],
    RUN_SCENARIOS,
    list()
)
"""List of (subfolder: str, num_cycles: int, cycle_index: int)."""

RUN_IDS = [f"{param[0]}, cycle{param[2]}" for param in RUN_PARAMS]


@mark.parametrize("subfolder, num_cycles, cycle_index", RUN_PARAMS, ids=RUN_IDS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
@patch(f"{utils_path}.related_cycles")
@patch(f"{biomass_utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_run(
    search_mock: MagicMock,
    get_cover_crop_property_terms_mock: MagicMock,
    related_cycles_mock: MagicMock,
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

    cycles = [
        _load_fixture(f"{fixtures_folder}/{subfolder}/cycle{i}.jsonld") for i in range(num_cycles)
    ]

    cycle["site"] = site
    related_cycles_mock.return_value = cycles

    result = run(cycle)
    assert order_list(result) == order_list(expected)

    assert get_cover_crop_property_terms_mock.call_count <= 1  # assert the API call is only requested once
    search_mock.assert_not_called()                            # assert the API call is properly mocked


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
@patch(f"{utils_path}.related_cycles")
@patch(f"{biomass_utils_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{term_path}.search")
def test_run_empty(
    search_mock: MagicMock,
    get_cover_crop_property_terms_mock: MagicMock,
    related_cycles_mock: MagicMock,
    _new_emission_mock: MagicMock
):
    """
    Test `run` function for each cycle in each scenario.
    """
    CYCLE = {}
    EXPECTED = []

    related_cycles_mock.return_value = [CYCLE]

    result = run(CYCLE)
    assert result == EXPECTED

    assert get_cover_crop_property_terms_mock.call_count <= 1  # assert the API call is only requested once
    search_mock.assert_not_called()                            # assert the API call is properly mocked
