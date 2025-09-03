from unittest.mock import patch
import json
from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.hestia.feedConversionRatio import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.feedConversionRatio"
fixtures_folder = f"{fixtures_path}/{MODEL}/feedConversionRatio"

TERMS_BY_ID = {
    'energyContentHigherHeatingValue': {'units': 'MJ / kg'}
}


def fake_download_term(term_id: str, *args): return TERMS_BY_ID.get(term_id, {'@id': term_id, 'units': '%'})


@patch(f"{class_path}.get_total_value_converted_with_min_ratio", return_value=10)
def test_should_run(*args):
    cycle = {'products': []}

    # without kg liveweight => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with kg liveweight => run
    cycle['products'] = [{
        'term': {
            'units': 'kg liveweight',
            'termType': TermTermType.ANIMALPRODUCT.value
        },
        'value': [10]
    }]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
@patch(f"{class_path}.is_run_required", return_value=True)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_term)
@patch(f"{class_path}.is_run_required", return_value=True)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_with_carcass(*args):
    with open(f"{fixtures_folder}/with-carcass/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-carcass/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
