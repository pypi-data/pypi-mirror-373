from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.akagiEtAl2011.utils import MODEL
from hestia_earth.models.akagiEtAl2011.pm25ToAirCropResidueBurning import TERM_ID, run

class_path_utils = f"hestia_earth.models.{MODEL}.utils"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path_utils}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path_utils}._new_emission", side_effect=fake_new_emission)
def test_run_data_complete(*args):
    with open(f"{fixtures_folder}/no-product-data-complete/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/no-product-data-complete/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
