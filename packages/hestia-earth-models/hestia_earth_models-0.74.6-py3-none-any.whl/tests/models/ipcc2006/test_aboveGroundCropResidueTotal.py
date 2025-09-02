import os
import json
from unittest.mock import patch
from pytest import mark
from hestia_earth.schema import TermTermType

from tests.utils import fixtures_path, fake_new_product
from hestia_earth.models.ipcc2006.aboveGroundCropResidueTotal import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}.get_node_property", return_value={'value': 10})
def test_should_run(*args):
    product_match_lookup = {'term': {'@id': 'genericCropSeed', 'termType': TermTermType.CROP.value}, 'value': [10]}
    product_no_match_lookup = {'term': {'@id': 'genericCropStraw', 'termType': TermTermType.CROP.value}, 'value': [10]}
    cycle = {'products': []}

    # with 1 crop matching lookup => run
    cycle['products'] = [product_match_lookup]
    should_run, *args = _should_run(cycle)
    assert should_run is True

    # with 1 crop not matching lookup => no run
    cycle['products'] = [product_no_match_lookup]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with 2 crops matching lookup => no run
    cycle['products'] = [product_match_lookup, product_match_lookup]
    should_run, *args = _should_run(cycle)
    assert not should_run


@mark.parametrize("folder", _folders)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_crop(mock_new_product, folder: str):
    with open(f"{fixtures_folder}/{folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected, folder
