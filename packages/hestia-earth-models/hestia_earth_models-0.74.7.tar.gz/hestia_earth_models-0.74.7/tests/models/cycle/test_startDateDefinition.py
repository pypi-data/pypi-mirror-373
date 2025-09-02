import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.startDateDefinition import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


def test_run_with_permanent_crop():
    with open(f"{fixtures_folder}/permanent-crop/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    result = run(data)
    assert result == 'one year prior'


def test_run_with_permanent_crop_last_day():
    with open(f"{fixtures_folder}/permanent-crop-last-day/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    result = run(data)
    assert result == 'start of year'


def test_run_with_temporary_crop():
    with open(f"{fixtures_folder}/temporary-crop/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    result = run(data)
    assert result == 'harvest of previous crop'
