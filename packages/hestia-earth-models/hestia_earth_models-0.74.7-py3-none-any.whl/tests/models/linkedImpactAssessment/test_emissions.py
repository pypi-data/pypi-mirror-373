import os
import json
from unittest.mock import patch
from tests.utils import fixtures_path, fake_new_emission, fake_load_impacts

from hestia_earth.models.linkedImpactAssessment.emissions import MODEL, run

class_path = f"hestia_earth.models.{MODEL}.emissions"
fixtures_folder = os.path.join(fixtures_path, MODEL, 'emissions')


@patch(F"{class_path}.load_impacts", side_effect=fake_load_impacts)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
