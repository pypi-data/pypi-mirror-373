from unittest.mock import patch
import json
from hestia_earth.schema import TermTermType

from tests.utils import fixtures_path, fake_new_product
from hestia_earth.models.hestia.liveAnimal import MODEL, MODEL_KEY, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@patch(f"{class_path}.get_liveAnimal_term_id", return_value='chicken')
@patch(f"{class_path}.valid_site_type", return_value=False)
@patch(f"{class_path}.find_primary_product", return_value=None)
def test_should_run(mock_primary_product, mock_valid_site_type, *args):
    cycle = {}

    # no primary product => no run
    mock_primary_product.return_value = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with primary product => not run
    product = {
        'term': {'termType': TermTermType.ANIMALPRODUCT.value},
        'value': [2]
    }
    mock_primary_product.return_value = product
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with valid siteType => not run
    mock_valid_site_type.return_value = True
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with product per head property => run
    product['properties'] = [{'term': {'@id': 'weightPerHead'}, 'value': 10}]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run(*argsm):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_carcass_weight(*argsm):
    with open(f"{fixtures_folder}/carcass-weight/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/carcass-weight/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
