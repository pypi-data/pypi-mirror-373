from unittest.mock import patch
import json
from tests.utils import fake_new_practice, fixtures_path
from hestia_earth.schema import TermTermType

from hestia_earth.models.hestia.cropResidueManagement import MODEL, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TermTermType.CROPRESIDUEMANAGEMENT.value}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TermTermType.CROPRESIDUEMANAGEMENT.value}"


@patch(f"{class_path}.has_residue_incorporated_practice", return_value=False)
def test_should_run(*args):
    # no practices => no run
    cycle = {'practices': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with practice at 50% => no run
    cycle['practices'] = [{'term': {'termType': TermTermType.CROPRESIDUEMANAGEMENT.value}, 'value': [50]}]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with practice at 100% => no run
    cycle['practices'] = [{'term': {'termType': TermTermType.CROPRESIDUEMANAGEMENT.value}, 'value': [100]}]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}.has_residue_incorporated_practice", return_value=False)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(data)
    assert result == expected


@patch(f"{class_path}.has_residue_incorporated_practice", return_value=True)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_with_residue_incorporated(*args):
    with open(f"{fixtures_folder}/with-incorporated-practice/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/with-incorporated-practice/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(data)
    assert result == expected
