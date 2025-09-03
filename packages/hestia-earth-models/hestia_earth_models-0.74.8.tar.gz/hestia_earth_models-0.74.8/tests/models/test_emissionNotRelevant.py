from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.emissionNotRelevant import MODEL, run

class_path = f"hestia_earth.models.{MODEL}"
fixtures_folder = f"{fixtures_path}/{MODEL}"


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_cropland(*args):
    with open(f"{fixtures_folder}/cropland/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/cropland/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run('all', cycle)
    assert result == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_pond(*args):
    with open(f"{fixtures_folder}/pond/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/pond/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run('all', cycle)
    assert result == expected
