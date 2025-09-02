from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.emepEea2019.nh3ToAirExcreta import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
model_utils_path = f"hestia_earth.models.{MODEL}.utils"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._is_term_type_complete")
def test_should_run(mock_is_complete, *args):
    cycle = {}

    # no complete => no run
    mock_is_complete.return_value = False
    should_run, *args = _should_run(cycle)
    assert not should_run

    # is complete => run
    mock_is_complete.return_value = True
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{model_utils_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
