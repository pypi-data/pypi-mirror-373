from unittest.mock import patch
import json

from tests.utils import fixtures_path, fake_new_product, order_list
from hestia_earth.models.hestia.excretaKgN import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.excretaKgN"
fixtures_folder = f"{fixtures_path}/{MODEL}/excretaKgN"


def test_should_run():
    cycle = {'@type': 'Cycle', 'products': []}

    # no products => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with only 1 excreta => run
    cycle['products'] = [{
        'term': {'termType': 'excreta', '@id': 'excretaKgMass', 'units': 'kg'},
        'value': [100]
    }]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert order_list(result) == order_list(expected)
