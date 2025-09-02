from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.cycle.animal.properties import MODEL_KEY, run

class_path = f"hestia_earth.models.cycle.animal.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/cycle/animal/{MODEL_KEY}"


@patch('hestia_earth.models.utils.feedipedia._new_property', side_effect=fake_new_property)
def test_run_with_min_max(*args):
    with open(f"{fixtures_folder}/with-min-max/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-min-max/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
