import json
import pytest
from tests.utils import fixtures_path

from hestia_earth.models.cycle.siteArea import MODEL, MODEL_KEY, _should_run, run

fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@pytest.mark.parametrize(
    'test_name,cycle,site,expected_should_run',
    [
        (
            'no animals => no run',
            {},
            {'siteType': 'animal housing'},
            False
        ),
        (
            'with animals => no run',
            {
                'animals': [{'term': {'termType': 'liveAnimal'}, 'value': 10}]
            },
            {'siteType': 'animal housing'},
            False
        ),
        (
            'with animals and stocking density => run',
            {
                'animals': [{'term': {'termType': 'liveAnimal'}, 'value': 10}],
                'practices': [{'term': {'@id': 'stockingDensityAnimalHousingAverage'}, 'value': [10]}]
            },
            {'siteType': 'animal housing'},
            True
        )
    ]
)
def test_should_run(test_name, cycle, site, expected_should_run):
    should_run = _should_run(cycle, site)
    assert should_run == expected_should_run, test_name


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    value = run(data)
    assert float(value) == float(expected)
