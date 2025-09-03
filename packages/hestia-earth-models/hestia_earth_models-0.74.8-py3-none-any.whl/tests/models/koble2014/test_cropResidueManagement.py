from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.koble2014.cropResidueManagement import MODEL, MODEL_KEY, run

fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@patch(f"hestia_earth.models.{MODEL}.utils._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
