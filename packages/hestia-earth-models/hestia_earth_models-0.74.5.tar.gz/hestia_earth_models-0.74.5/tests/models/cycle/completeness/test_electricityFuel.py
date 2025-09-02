import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.completeness.electricityFuel import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.cycle.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/cycle/{MODEL}/{MODEL_KEY}"


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    assert run(cycle) is True


def test_run_invalid():
    with open(f"{fixtures_folder}/cycle-invalid.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    assert not run(cycle)
