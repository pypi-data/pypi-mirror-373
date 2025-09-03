from unittest.mock import patch
import json

from tests.utils import fixtures_path, fake_new_practice
from hestia_earth.models.hestia.residueRemoved import MODEL, TERM_ID, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_by_products(*args):
    with open(f"{fixtures_folder}/by-products/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/by-products/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_by_practices(*args):
    with open(f"{fixtures_folder}/by-practices/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/by-practices/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
