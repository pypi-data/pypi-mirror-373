from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.pooreNemecek2018.freshwaterWithdrawalsDuringCycle import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._get_irrigation", return_value=None)
@patch(f"{class_path}.get_product", return_value={})
def test_should_run(mock_product, mock_irrigation):
    impact = {}

    # with a product => no run
    mock_product.return_value = {'term': {'@id': 'product'}, 'economicValueShare': 10}
    should_run, *args = _should_run(impact)
    assert not should_run

    # with irrigation => run
    mock_irrigation.return_value = 10
    should_run, *args = _should_run(impact)
    assert should_run is True


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_data_complete(*args):
    with open(f"{fixtures_folder}/data-complete/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/data-complete/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_with_waterRegime(*args):
    with open(f"{fixtures_folder}/with-waterRegime/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/with-waterRegime/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
