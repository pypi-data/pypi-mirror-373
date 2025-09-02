import json
from pytest import mark
from unittest.mock import MagicMock, patch

from hestia_earth.models.ipcc2019.n2OToAirOrganicSoilCultivationDirect import MODEL, TERM_ID, _should_run, run
from tests.utils import fake_new_emission, fixtures_path

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

# subfolder, should_run
PARAMS_SHOULD_RUN = [
    ("acacia", True),
    ("annual-crops", True),
    ("grassland", True),
    ("oil-palm", True),
    ("other", False),
    ("paddy-rice-cultivation", True),
    ("perennial-crops", True),
    ("sago-palm", True),
    ("polar", False),
    ("mineral-soil", True),
    ("unknown-soil", False),
    ("unknown-land-occupation", False),
    ("unknown-eco-climate-zone", False)  # Closes 1233
]
IDS_SHOULD_RUN = [p[0] for p in PARAMS_SHOULD_RUN]


@mark.parametrize("subfolder, expected", PARAMS_SHOULD_RUN, ids=IDS_SHOULD_RUN)
def test_should_run(
    subfolder: str,
    expected: bool
):
    folder = f"{fixtures_folder}/{subfolder}"

    with open(f"{folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    result, *_ = _should_run(cycle)
    assert result == expected


PARAMS_RUN = [subfolder for subfolder, should_run in PARAMS_SHOULD_RUN if should_run]


@mark.parametrize("subfolder", PARAMS_RUN,)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(
    _mock_new_emission: MagicMock,
    subfolder: str
):
    folder = f"{fixtures_folder}/{subfolder}"

    with open(f"{folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
