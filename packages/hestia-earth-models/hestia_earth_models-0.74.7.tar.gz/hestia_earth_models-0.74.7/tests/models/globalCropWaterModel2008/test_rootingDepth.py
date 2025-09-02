from unittest.mock import patch
import json
from hestia_earth.schema import CycleFunctionalUnit
from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.globalCropWaterModel2008.rootingDepth import (
    MODEL, TERM_ID, run, _should_run, _should_run_product
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"
TERMS = [
    'waterPumpedGroundwater',
    'waterBrackish',
    'waterSourceUnspecified'
]


def fake_download_term(node_id, *args):
    return {"@type": "Term", "@id": node_id}


@patch(f"{class_path}.get_irrigation_terms", return_value=TERMS)
def test_should_run(*args):
    cycle = {'products': []}

    # relative unit => no run
    cycle['functionalUnit'] = CycleFunctionalUnit.RELATIVE.value
    should_run, *args = _should_run(cycle)
    assert not should_run

    # 1 ha => no run
    cycle['functionalUnit'] = CycleFunctionalUnit._1_HA.value
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with crops => run
    cycle['products'] = [{'term': {'termType': 'crop'}}]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}.get_irrigation_terms", return_value=TERMS)
@patch(f"{class_path}._get_value")
def test_should_run_product(mock_get_value, *args):
    product = {}

    # no value => no run
    mock_get_value.return_value = None
    should_run, *args = _should_run_product({})(product)
    assert not should_run

    # product with model => does not run
    mock_get_value.return_value = 10
    should_run, *args = _should_run_product({})(product)
    assert should_run is True


@patch(f"{class_path}.get_irrigation_terms", return_value=TERMS)
@patch(f"{class_path}.download_term", side_effect=fake_download_term)
@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.get_irrigation_terms", return_value=TERMS)
@patch(f"{class_path}.download_term", side_effect=fake_download_term)
@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_gap_fill_with_irrigation(*args):
    with open(f"{fixtures_folder}/with-irrigation/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-irrigation/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
