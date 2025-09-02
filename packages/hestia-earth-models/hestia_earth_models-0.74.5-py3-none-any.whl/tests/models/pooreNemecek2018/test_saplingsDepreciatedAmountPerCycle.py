from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_input

from hestia_earth.models.pooreNemecek2018.saplingsDepreciatedAmountPerCycle import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.find_term_match", return_value={'value': [10]})
@patch(f"{class_path}.get_crop_lookup_value", return_value=10)
@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
def test_should_run(mock_is_term_type_incomplete, *args):
    cycle = {'cycleDuration': 200, 'products': [{'term': {'@id': 'wheatGrain'}}]}

    mock_is_term_type_incomplete.return_value = False
    should_run, *args = _should_run(cycle)
    assert not should_run

    mock_is_term_type_incomplete.return_value = True
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run_no_plantation(*args):
    with open(f"{fixtures_folder}/no-orchard-crop/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    value = run(cycle)
    assert value == []
