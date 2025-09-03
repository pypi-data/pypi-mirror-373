import json
from unittest.mock import patch

from hestia_earth.models.environmentalFootprintV3_1 import MODEL_FOLDER
from hestia_earth.models.environmentalFootprintV3_1.freshwaterEcotoxicityPotentialCtue import TERM_ID, run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL_FOLDER}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL_FOLDER}/{TERM_ID}"


with open(f"{fixtures_path}/impact_assessment/emissions/impact-assessment.jsonld", encoding='utf-8') as f:
    impact = json.load(f)


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    impact['cycle'] = cycle
    value = run(impact)
    assert value == expected
