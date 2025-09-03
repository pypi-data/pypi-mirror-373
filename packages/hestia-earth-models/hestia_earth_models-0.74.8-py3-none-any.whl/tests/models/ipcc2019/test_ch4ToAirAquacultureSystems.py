import json
import pytest
from unittest.mock import patch
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019.ch4ToAirAquacultureSystems import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@pytest.mark.parametrize(
    'test_name,cycle,expected_should_run',
    [
        (
            'no cycleDuration => no run',
            {},
            False
        ),
        (
            'with cycleDuration not relative unit => no run',
            {'cycleDuration': 150, 'functionalUnit': '1 ha'},
            False
        ),
        (
            'with cycleDuration, relative unit, no area => no run',
            {'cycleDuration': 150, 'functionalUnit': 'relative'},
            False
        ),
        (
            'with cycleDuration, relative unit, with area, no measurement => no run',
            {'cycleDuration': 150, 'functionalUnit': 'relative', 'site': {'area': 1000}},
            False
        ),
        (
            'with cycleDuration, relative unit, with area, and measurement => run',
            {
                'cycleDuration': 150,
                'functionalUnit': 'relative',
                'site': {'area': 1000, 'measurements': [{'term': {'@id': 'salineWater', 'termType': 'measurement'}}]}
            },
            True
        )
    ]
)
def test_should_run(test_name, cycle, expected_should_run):
    should_run, *args = _should_run(cycle)
    assert should_run == expected_should_run, test_name


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
