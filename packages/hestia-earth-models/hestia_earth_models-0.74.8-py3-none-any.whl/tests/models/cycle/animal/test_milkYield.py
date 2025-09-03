import json

from tests.utils import fixtures_path
from hestia_earth.models.cycle.animal.milkYield import MODEL, MODEL_KEY, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.animal.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/animal/{MODEL_KEY}"


def test_should_run():
    # without liveAnimal => no run
    cycle = {'animals': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with liveAnimal => run
    cycle = {'animals': [{'term': {'termType': 'liveAnimal'}}]}
    should_run, *args = _should_run(cycle)
    assert should_run is True


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
