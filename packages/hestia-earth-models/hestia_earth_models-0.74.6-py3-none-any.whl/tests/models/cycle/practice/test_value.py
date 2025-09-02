import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.practice.value import run, _should_run

class_path = 'hestia_earth.models.cycle.practice.value'
fixtures_folder = f"{fixtures_path}/cycle/practice/value"


def test_should_run():
    practice = {}

    # without min/max => no run
    assert not _should_run({})(practice)

    # with min and max and value => no run
    practice = {
        'min': [5],
        'max': [50],
        'value': [25]
    }
    assert not _should_run({})(practice)

    # with min and max but not value => run
    practice = {
        'min': [5],
        'max': [10],
        'value': []
    }
    assert _should_run({})(practice) is True


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


def test_run_defaultValue():
    with open(f"{fixtures_folder}/lookup-defaultValue/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/lookup-defaultValue/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
