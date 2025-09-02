from unittest.mock import patch
import json
from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.transformation.product.excreta import MODEL, MODEL_KEY, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/product/{MODEL_KEY}"


def test_should_run():
    transformation = {'@type': 'Transformation', 'term': {}}

    # not an excreta management => no run
    transformation['term']['termType'] = TermTermType.ANIMALMANAGEMENT.value
    assert not _should_run(transformation)

    # is an excreta management => no run
    transformation['term']['termType'] = TermTermType.EXCRETAMANAGEMENT.value
    assert _should_run(transformation) is True


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_same_id(*args):
    with open(f"{fixtures_folder}/product-same-id/transformation.jsonld", encoding='utf-8') as f:
        transformation = json.load(f)

    with open(f"{fixtures_folder}/product-same-id/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(transformation)
    assert result == expected


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_different_id(*args):
    with open(f"{fixtures_folder}/product-different-id/transformation.jsonld", encoding='utf-8') as f:
        transformation = json.load(f)

    with open(f"{fixtures_folder}/product-different-id/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(transformation)
    assert result == expected


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_no_input_value(*args):
    with open(f"{fixtures_folder}/no-input-value/transformation.jsonld", encoding='utf-8') as f:
        transformation = json.load(f)

    result = run(transformation)
    assert result == []
