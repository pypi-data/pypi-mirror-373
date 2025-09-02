import os
import json
from unittest.mock import patch

from tests.utils import fixtures_path, fake_new_emission
from hestia_earth.models.ecoalimV9.cycle import MODEL, run

class_path = f"hestia_earth.models.{MODEL}.cycle"
fixtures_folder = os.path.join(fixtures_path, MODEL, 'cycle')


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)['emissions']

    result = run(cycle)
    assert result == expected
