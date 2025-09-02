import json
import pytest
from tests.utils import fixtures_path

from hestia_earth.models.cycle.otherSitesUnusedDuration import MODEL, MODEL_KEY, _should_run, run

fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@pytest.mark.parametrize(
    'test_name,cycle,expected_should_run',
    [
        (
            'no otherSites => no run',
            {},
            False
        ),
        (
            'with otherSites => no run',
            {
                'otherSites': [{'siteType': 'cropland'}, {'siteType': 'permanent pasture'}]
            },
            False
        ),
        (
            'with otherSites and otherSitesDuration => no run',
            {
                'otherSites': [{'siteType': 'cropland'}, {'siteType': 'permanent pasture'}],
                'otherSitesDuration': [200, 300]
            },
            False
        ),
        (
            'with siteDuration and otherSitesDuration and longFallowRatio => run',
            {
                'otherSites': [{'@id': '1', 'siteType': 'cropland'}, {'@id': '2', 'siteType': 'permanent pasture'}],
                'otherSitesDuration': [200, 300],
                'practices': [{'term': {'@id': 'longFallowRatio'}, 'value': [10], 'site': {'@id': '1'}}]
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

    value = run(data)
    assert value == [50, None]
