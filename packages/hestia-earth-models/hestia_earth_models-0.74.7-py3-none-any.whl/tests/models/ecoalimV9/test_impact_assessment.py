import os
import json
from unittest.mock import patch

from tests.utils import fixtures_path, fake_new_indicator
from hestia_earth.models.ecoalimV9.impact_assessment import MODEL, run

class_path = f"hestia_earth.models.{MODEL}.impact_assessment"
fixtures_folder = os.path.join(fixtures_path, MODEL, 'impact_assessment')


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact.jsonld", encoding='utf-8') as f:
        impact = json.load(f)
    with open(os.path.join(fixtures_path, MODEL, 'cycle', 'cycle.jsonld'), encoding='utf-8') as f:
        cycle = json.load(f)
    impact['cycle'] = cycle

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)['emissionsResourceUse']

    result = run(impact)
    assert result == expected
