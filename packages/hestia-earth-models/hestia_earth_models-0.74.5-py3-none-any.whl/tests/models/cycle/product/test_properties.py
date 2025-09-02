import json
from unittest.mock import patch
from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.cycle.product.properties import MODEL_KEY, run

class_path = f"hestia_earth.models.cycle.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/cycle/product/{MODEL_KEY}"


@patch('hestia_earth.models.utils.feedipedia._new_property', side_effect=fake_new_property)
def test_run_with_dryMatter(*args):
    with open(f"{fixtures_folder}/with-dryMatter/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-dryMatter/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch('hestia_earth.models.utils.feedipedia._new_property', side_effect=fake_new_property)
def test_run_with_min_max(*args):
    with open(f"{fixtures_folder}/with-min-max/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-min-max/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
