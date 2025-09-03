from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.hestia.aboveGroundCropResidueTotal import MODEL, TERM_ID, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_no_match(*args):
    with open(f"{fixtures_folder}/no-match/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    value = run(cycle)
    assert value == []


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_with_100_percent(*args):
    with open(f"{fixtures_folder}/with-practice-100/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-practice-100/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
