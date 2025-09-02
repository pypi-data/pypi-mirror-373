from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.hestia.irrigatedTypeUnspecified import MODEL, TERM_ID, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_irrigated(*argsm):
    with open(f"{fixtures_folder}/with-waterRegime/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    value = run(cycle)
    assert value == []


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_complete_low_irrigation(*argsm):
    with open(f"{fixtures_folder}/complete-low-irrigation/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    value = run(cycle)
    assert value == []


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_complete_high_irrigation(*argsm):
    with open(f"{fixtures_folder}/complete-high-irrigation/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/complete-high-irrigation/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_incomplete_low_irrigation(*argsm):
    with open(f"{fixtures_folder}/incomplete-low-irrigation/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    value = run(cycle)
    assert value == []


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_incomplete_high_irrigation(*argsm):
    with open(f"{fixtures_folder}/incomplete-high-irrigation/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/incomplete-high-irrigation/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
