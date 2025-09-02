import json
import pytest
from tests.utils import fixtures_path

from hestia_earth.models.cycle import MODEL
from hestia_earth.models.cycle.otherSitesArea import MODEL_KEY, run, _should_run

fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@pytest.mark.parametrize(
    'test_name,cycle,expected_should_run',
    [
        (
            'no animals => no run',
            {},
            False
        ),
        (
            'with animals => no run',
            {
                'animals': [{'term': {'termType': 'liveAnimal'}, 'value': 10}]
            },
            False
        ),
        (
            'with animals and otherSites => no run',
            {
                'animals': [{'term': {'termType': 'liveAnimal'}, 'value': 10}],
                'otherSites': [{'siteType': 'animal housing'}]
            },
            False
        ),
        (
            'with animals, otherSites and stocking density => run',
            {
                'animals': [{'term': {'termType': 'liveAnimal'}, 'value': 10}],
                'otherSites': [{'siteType': 'animal housing'}],
                'practices': [{'term': {'@id': 'stockingDensityAnimalHousingAverage'}, 'value': [10]}]
            },
            True
        ),
        (
            'with multiple animal housing sites => no run',
            {
                'animals': [{'term': {'termType': 'liveAnimal'}, 'value': 10}],
                'site': {'siteType': 'animal housing'},
                'otherSites': [{'siteType': 'animal housing'}],
                'practices': [{'term': {'@id': 'stockingDensityAnimalHousingAverage'}, 'value': [10]}]
            },
            False
        )
    ]
)
def test_should_run(test_name, cycle, expected_should_run):
    should_run = _should_run(cycle)
    assert should_run == expected_should_run, test_name


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    value = run(data)
    assert value == [float(expected), None]
