from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.ipcc2019 import MODEL
from hestia_earth.models.ipcc2019.animal.milkYieldPerAnimal import MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.animal.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/animal/{MODEL_KEY}"


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
