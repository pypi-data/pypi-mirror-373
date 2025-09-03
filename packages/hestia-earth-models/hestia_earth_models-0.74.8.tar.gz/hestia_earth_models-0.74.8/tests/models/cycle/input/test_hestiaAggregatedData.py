import os
import json
from unittest.mock import patch
from hestia_earth.schema import TermTermType

from tests.utils import fake_closest_impact_id, fixtures_path
from hestia_earth.models.cycle.input.hestiaAggregatedData import MODEL_ID, run, _should_run, _should_run_seed

class_path = f"hestia_earth.models.cycle.input.{MODEL_ID}"
fixtures_folder = os.path.join(fixtures_path, 'cycle', 'input', MODEL_ID)

GENERIC_CROP = {'@id': 'genericCropSeed', 'name': 'Generic crop, seed'}


def _fake_generic_closest_impact_id(product_id: str, **kwargs):
    return 'genericCropSeed-world-2000-2009' if product_id == GENERIC_CROP['@id'] else None


def test_should_run():
    cycle = {}

    # no inputs => no run
    cycle['inputs'] = []
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with inputs and no impactAssessment => no run
    cycle['inputs'] = [{}]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with endDate => run
    cycle['endDate'] = {'2019'}
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}.get_generic_crop", return_value=GENERIC_CROP)
@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.find_primary_product", return_value={})
def test_should_run_seed(mock_primary_product, *args):
    cycle = {}

    # with a crop product => no run
    mock_primary_product.return_value = {'term': {'termType': TermTermType.CROP.value}}
    should_run, *args = _should_run_seed(cycle)
    assert not should_run

    # with a seed input => run
    cycle['inputs'] = [{'term': {'@id': 'seed', 'termType': 'seed'}}]
    should_run, *args = _should_run_seed(cycle)
    assert should_run is True


@patch(f"{class_path}.get_generic_crop", return_value=GENERIC_CROP)
@patch('hestia_earth.models.utils.aggregated.find_closest_impact_id', side_effect=fake_closest_impact_id)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_generic_crop", return_value=GENERIC_CROP)
@patch(f"{class_path}.find_closest_impact_id", side_effect=fake_closest_impact_id)
def test_run_seed(*args):
    with open(f"{fixtures_folder}/seed/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/seed/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.get_generic_crop", return_value=GENERIC_CROP)
@patch(f"{class_path}.find_closest_impact_id", side_effect=_fake_generic_closest_impact_id)
def test_run_seed_generic(*args):
    with open(f"{fixtures_folder}/seed-generic/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/seed-generic/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
