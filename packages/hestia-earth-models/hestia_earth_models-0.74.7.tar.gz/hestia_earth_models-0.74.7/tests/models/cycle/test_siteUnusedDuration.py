import json
import pytest
from tests.utils import fixtures_path

from hestia_earth.models.cycle.siteUnusedDuration import MODEL, MODEL_KEY, _should_run, run

fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@pytest.mark.parametrize(
    'test_name,cycle,expected_should_run',
    [
        (
            'no siteDuration => no run',
            {},
            False
        ),
        (
            'with siteDuration => no run',
            {'siteDuration': 100},
            False
        ),
        (
            'with siteDuration and longFallowRatio => no run',
            {
                'siteDuration': 100,
                'practices': [{'term': {'@id': 'longFallowRatio'}, 'value': [10]}]
            },
            False
        ),
        (
            'with siteDuration and longFallowRatio and cropland => run',
            {
                'siteDuration': 100,
                'practices': [{'term': {'@id': 'longFallowRatio'}, 'value': [10]}],
                'site': {'siteType': 'cropland'}
            },
            True
        )
    ]
)
def test_should_run_animal(test_name, cycle, expected_should_run):
    should_run, *args = _should_run(cycle)
    assert should_run == expected_should_run, test_name


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    value = run(data)
    assert float(value) == float(expected)
