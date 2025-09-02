from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_input

from hestia_earth.models.hestia.inorganicFertiliser import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*argsm):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
