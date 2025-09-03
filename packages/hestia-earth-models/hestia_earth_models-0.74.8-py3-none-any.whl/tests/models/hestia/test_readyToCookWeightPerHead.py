from unittest.mock import patch
import json

from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.hestia.readyToCookWeightPerHead import MODEL, TERM_ID, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    cycle = {}

    # no animal products => run
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with animal products => no run
    cycle['products'] = [
        {
            'term': {
                'termType': TermTermType.ANIMALPRODUCT.value,
                'units': 'kg cold carcass weight'
            },
            'properties': [
                {'term': {'@id': 'liveweightPerHead'}},
                {'term': {'@id': 'processingConversionLiveweightToReadyToCookWeight'}}
            ]
        }
    ]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch("hestia_earth.models.utils.property.download_term", return_value={'units': '%'})
@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
