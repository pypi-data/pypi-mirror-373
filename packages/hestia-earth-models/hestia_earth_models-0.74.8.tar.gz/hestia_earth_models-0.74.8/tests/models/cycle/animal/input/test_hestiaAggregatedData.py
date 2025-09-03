import json
from unittest.mock import patch

from tests.utils import fake_closest_impact_id, fixtures_path
from hestia_earth.models.cycle.animal.input.hestiaAggregatedData import MODEL_ID, run, _should_run_animal

class_path = f"hestia_earth.models.cycle.animal.input.{MODEL_ID}"
fixtures_folder = f"{fixtures_path}/cycle/animal/input/{MODEL_ID}"


def test_should_run():
    cycle = {}
    animal = {}

    # no inputs => no run
    animal['inputs'] = []
    should_run, *args = _should_run_animal(cycle, animal)
    assert not should_run

    # with inputs and no impactAssessment => no run
    animal['inputs'] = [{}]
    should_run, *args = _should_run_animal(cycle, animal)
    assert not should_run

    # with endDate => run
    cycle['endDate'] = {'2019'}
    should_run, *args = _should_run_animal(cycle, animal)
    assert should_run is True


@patch('hestia_earth.models.utils.aggregated.find_closest_impact_id', side_effect=fake_closest_impact_id)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
