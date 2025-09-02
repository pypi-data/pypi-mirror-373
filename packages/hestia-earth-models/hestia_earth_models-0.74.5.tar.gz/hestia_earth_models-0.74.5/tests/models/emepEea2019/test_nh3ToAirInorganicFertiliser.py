from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.emepEea2019.nh3ToAirInorganicFertiliser import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
model_utils_path = f"hestia_earth.models.{MODEL}.utils"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.find_term_match", return_value={'value': [10]})
@patch(f"{class_path}.most_relevant_measurement_value", return_value=0)
def test_should_run(mock_measurement, *args):
    # no measurements => no run
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with measurements => no run
    mock_measurement.return_value = 10
    should_run, *args = _should_run(cycle)
    assert not should_run

    # is complete => run
    cycle['completeness'] = {'fertiliser': True}
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


@patch(f"{model_utils_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_unspecified(*args):
    with open(f"{fixtures_folder}/with-unspecified/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-unspecified/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{model_utils_path}._new_emission", side_effect=fake_new_emission)
def test_run_complete(*args):
    with open(f"{fixtures_folder}/is-complete/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/is-complete/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
