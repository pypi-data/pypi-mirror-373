import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.transformation import MODEL, MODEL_KEY, run

fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
