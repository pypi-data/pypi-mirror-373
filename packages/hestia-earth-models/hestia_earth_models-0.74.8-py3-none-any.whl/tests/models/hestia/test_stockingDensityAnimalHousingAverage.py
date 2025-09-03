from unittest.mock import patch
import pytest
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.hestia.stockingDensityAnimalHousingAverage import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@pytest.mark.parametrize(
    'test_name,cycle,expected_should_run',
    [
        (
            'no live animal => no run',
            {'animals': [{'term': {'termType': 'crop'}, 'value': 10}]},
            False
        ),
        (
            'with live animal => run',
            {'animals': [{'term': {'termType': 'liveAnimal'}, 'value': 10}]},
            True
        ),
    ]
)
@patch(f"{class_path}.get_lookup_value", return_value=10)
def test_should_run(mock_lookup, test_name, cycle, expected_should_run):
    should_run, *args = _should_run(cycle)
    assert should_run == expected_should_run, test_name


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
