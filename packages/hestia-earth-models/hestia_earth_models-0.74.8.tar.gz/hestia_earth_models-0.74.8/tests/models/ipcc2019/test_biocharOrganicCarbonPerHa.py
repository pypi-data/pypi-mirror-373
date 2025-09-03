import json
from os.path import isfile
from pytest import mark
from unittest.mock import MagicMock, patch

from hestia_earth.models.ipcc2019.biocharOrganicCarbonPerHa import _should_run, MODEL, run, TERM_ID

from tests.utils import fake_new_measurement, fixtures_path

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
property_path = "hestia_earth.models.utils.property"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

_DEFAULT_PROPERTIES = {
    "biocharManureGasification": {
        "organicCarbonContent": {
            "value": 9,
            "sd": 2.4,
            "min": 0,
            "max": 100
        }
    },
    "biocharBambooLowTemperaturePyrolysis": {
        "organicCarbonContent": {
            "value": 77,
            "sd": 16.5,
            "min": 0,
            "max": 100
        }
    },
    "biocharStrawHighTemperaturePyrolysis": {
        "organicCarbonContent": {
            "value": 65,
            "sd": 14.9,
            "min": 0,
            "max": 100
        }
    },
    "biocharPaperSludgeMediumTemperaturePyrolysis": {
        "organicCarbonContent": {
            "value": 35,
            "sd": 7.1,
            "min": 0,
            "max": 100
        }
    },
    "biocharUnspecifiedFeedstockUnspecifiedProductionMethod": {
        "organicCarbonContent": {
            "value": 40.6,
            "sd": 10.5,
            "min": 0,
            "max": 100
        }
    }
}


def fake_find_term_property(term: dict, property: str, *_):
    term_id = term.get('@id', None)
    return _DEFAULT_PROPERTIES.get(term_id, {}).get(property, {})


def _load_fixture(path: str, default=None):
    if isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


# subfolder, should_run
PARAMS_SHOULD_RUN = [
    ("with-stats", True),
    ("no-biochar", True),
    ("no-cycles", False),
    ("with-organic-soils", False),
    ("with-relative-func-unit", False),
    ("with-site-type-forest", False),
    ("with-missing-start-dates", True)
]
IDS_SHOULD_RUN = [p[0] for p in PARAMS_SHOULD_RUN]


@mark.parametrize("subfolder, should_run", PARAMS_SHOULD_RUN, ids=IDS_SHOULD_RUN)
@patch(f"{property_path}.find_term_property", side_effect=fake_find_term_property)
@patch(f"{property_path}.download_term")
@patch(f"{class_path}.related_cycles")
def test_should_run(
    related_cycles_mock: MagicMock,
    download_term_mock: MagicMock,
    _find_term_property_mock: MagicMock,
    subfolder: str,
    should_run: bool
):
    folder = f"{fixtures_folder}/{subfolder}"

    site = _load_fixture(f"{folder}/site.jsonld", {})
    related_cycles_mock.return_value = _load_fixture(f"{folder}/cycles.jsonld", [])

    result, *_ = _should_run(site)
    assert result == should_run

    # Ensure that the property utils are properly mocked.
    download_term_mock.assert_not_called()


PARAMS_RUN = [subfolder for subfolder, should_run in PARAMS_SHOULD_RUN if should_run]


@mark.parametrize("subfolder", PARAMS_RUN)
@patch(f"{property_path}.find_term_property", side_effect=fake_find_term_property)
@patch(f"{property_path}.download_term")
@patch(f"{class_path}.related_cycles")
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(
    _new_measurement_mock: MagicMock,
    related_cycles_mock: MagicMock,
    download_term_mock: MagicMock,
    _find_term_property_mock: MagicMock,
    subfolder: str
):
    folder = f"{fixtures_folder}/{subfolder}"

    site = _load_fixture(f"{folder}/site.jsonld", {})
    related_cycles_mock.return_value = _load_fixture(f"{folder}/cycles.jsonld", [])

    expected = _load_fixture(f"{folder}/result.jsonld", [])

    result = run(site)
    assert result == expected

    # Ensure that the property utils are properly mocked.
    download_term_mock.assert_not_called()
