import json
import pytest
from tests.utils import fixtures_path

from hestia_earth.models.cycle.siteDuration import MODEL, MODEL_KEY, _should_run, run

fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@pytest.mark.parametrize(
    'test_name,cycle,expected_should_run',
    [
        (
            'no cycleDuration => no run',
            {},
            False
        ),
        (
            'with otherSites => no run',
            {'otherSites': []},
            False
        ),
        (
            'with cycleDuration => run',
            {'cycleDuration': 100},
            True
        ),
        (
            'with a crop product and wrong startDateDefinition => no run',
            {
                'cycleDuration': 100,
                'products': [{'term': {'termType': 'crop'}, 'primary': True}],
                'startDateDefinition': 'random definition'
            },
            False
        ),
        (
            'with a crop product and correct startDateDefinition => run',
            {
                'cycleDuration': 100,
                'products': [{'term': {'termType': 'crop'}, 'primary': True}],
                'startDateDefinition': 'harvest of previous crop'
            },
            True
        )
    ]
)
def test_should_run_animal(test_name, cycle, expected_should_run):
    should_run = _should_run(cycle)
    assert should_run == expected_should_run, test_name


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    value = run(data)
    assert float(value) == float(expected)


def test_run_temporary_crop():
    with open(f"{fixtures_folder}/temporary-crop/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    value = run(data)
    assert float(value) == float(expected)


def test_run_permanent_crop():
    with open(f"{fixtures_folder}/permanent-crop/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    value = run(data)
    assert float(value) == float(expected)
