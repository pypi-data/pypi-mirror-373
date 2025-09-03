from unittest.mock import patch
import json

from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.ipcc2019.belowGroundCropResidue import (
    MODEL, TERM_ID, run, _should_run, _should_run_product
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

CROP_RESIDUE_TERM = {
    'termType': TermTermType.CROPRESIDUE.value
}


@patch('hestia_earth.models.utils.completeness.download_term', return_value=CROP_RESIDUE_TERM)
@patch(f"{class_path}._should_run_product", return_value=True)
def test_should_run(*args):
    crop_product = {'term': {'termType': TermTermType.CROP.value}}
    cycle = {'products': []}

    # no crops => no run
    cycle['products'] = []
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with a crop => run
    cycle['products'] = [crop_product]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch('hestia_earth.models.utils.completeness.download_term', return_value=CROP_RESIDUE_TERM)
@patch(f"{class_path}.get_yield_dm", return_value=None)
def test_should_run_product(mock_get_yield_dm, *args):
    product = {'term': {'@id': 'maizeGrain'}}

    # with a dryMatter property => no run
    product['properties'] = [{'term': {'@id': 'dryMatter'}, 'value': 10}]
    assert not _should_run_product(product)

    # with a value => no run
    product['value'] = [10]
    assert not _should_run_product(product)

    # with a lookup value => run
    mock_get_yield_dm.return_value = 10
    assert _should_run_product(product) is True


@patch('hestia_earth.models.utils.completeness.download_term', return_value=CROP_RESIDUE_TERM)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_crop(*args):
    with open(f"{fixtures_folder}/crop/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/crop/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch('hestia_earth.models.utils.completeness.download_term', return_value=CROP_RESIDUE_TERM)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_forage(*args):
    with open(f"{fixtures_folder}/forage/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/forage/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
