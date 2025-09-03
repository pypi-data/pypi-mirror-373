from unittest.mock import patch
import json
import os

from tests.utils import fixtures_path, fake_new_emission, fake_new_product, fake_new_input
from hestia_earth.orchestrator.models.transformations import run, _include_practice

folder_path = os.path.join(fixtures_path, 'orchestrator', 'transformation')


@patch('hestia_earth.orchestrator.strategies.merge._merge_version', return_value='0.0.0')
@patch('hestia_earth.models.transformation.input.excreta._new_input', side_effect=fake_new_input)
@patch('hestia_earth.models.transformation.product.excreta._new_product', side_effect=fake_new_product)
@patch('hestia_earth.models.ipcc2019.n2OToAirExcretaDirect._new_emission', side_effect=fake_new_emission)
def test_run(*args):
    with open(os.path.join(folder_path, 'config.json'), encoding='utf-8') as f:
        config = json.load(f)
    with open(os.path.join(folder_path, 'cycle.jsonld'), encoding='utf-8') as f:
        cycle = json.load(f)
    with open(os.path.join(folder_path, 'result.jsonld'), encoding='utf-8') as f:
        expected = json.load(f)

    result = run(config.get('models'), cycle)
    assert result == expected


def test_include_practice():
    term = {'@id': 'genericCropProduct', 'termType': 'crop'}
    assert not _include_practice({'term': term})

    term = {'@id': 'yieldOfPrimaryAquacultureProductLiveweightPerM2', 'termType': 'aquacultureManagement'}
    assert _include_practice({'term': term}) is True
