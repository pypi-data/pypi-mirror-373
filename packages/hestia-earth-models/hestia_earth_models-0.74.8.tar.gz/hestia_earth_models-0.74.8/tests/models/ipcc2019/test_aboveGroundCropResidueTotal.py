import os
import json
from unittest.mock import patch
from pytest import mark
from hestia_earth.schema import TermTermType

from tests.utils import fixtures_path, fake_new_product
from hestia_earth.models.ipcc2019.aboveGroundCropResidueTotal import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]

CROP_RESIDUE_TERM = {
    'termType': TermTermType.CROPRESIDUE.value
}


@patch('hestia_earth.models.utils.completeness.download_term', return_value=CROP_RESIDUE_TERM)
@patch(f"{class_path}._should_run_product", return_value=True)
def test_should_run(*args):
    crop_product = {
        'term': {'termType': TermTermType.CROP.value, '@id': 'wheatGrain'},
        'value': [10],
        'properties': [{'term': {'@id': 'dryMatter'}, 'value': 10}]
    }
    cycle = {'products': []}

    # no crops => no run
    cycle['products'] = []
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with a crop => run
    cycle['products'] = [crop_product]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@mark.parametrize("folder", _folders)
@patch('hestia_earth.models.utils.completeness.download_term', return_value=CROP_RESIDUE_TERM)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_crop(mock_new_product, mock_download_term, folder: str):
    with open(f"{fixtures_folder}/{folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected, folder
