import json
import os
from unittest.mock import patch
from pytest import mark

from hestia_earth.models.environmentalFootprintV3_1 import MODEL_FOLDER
from hestia_earth.models.environmentalFootprintV3_1.scarcityWeightedWaterUse import MODEL, TERM_ID, run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL_FOLDER}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL_FOLDER}/{TERM_ID}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


def fake_rounded_indicator(value: float):
    indicator = fake_new_indicator(TERM_ID, MODEL)
    indicator['value'] = round(value, 13)
    return indicator


@mark.parametrize("folder", _folders)
@patch(f"{class_path}._indicator", side_effect=fake_rounded_indicator)
def test_run(mock_indicator, folder):
    with open(f"{fixtures_folder}/{folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    expected = None
    if os.path.exists(f"{fixtures_folder}/{folder}/result.jsonld"):
        with open(f"{fixtures_folder}/{folder}/result.jsonld", encoding='utf-8') as f:
            expected = json.load(f)

    value = run(impactassessment)
    assert value == expected, folder
