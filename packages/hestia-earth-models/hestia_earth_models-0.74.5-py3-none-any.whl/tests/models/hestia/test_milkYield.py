from unittest.mock import patch
import json
from hestia_earth.schema import TermTermType

from tests.utils import fixtures_path, fake_new_practice
from hestia_earth.models.hestia.milkYield import MODEL, MODEL_KEY, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@patch(f"{class_path}.get_liveAnimal_term_id", return_value='chicken')
@patch(f"{class_path}.get_lookup_value", return_value='id')
@patch(f"{class_path}.valid_site_type", return_value=False)
def test_should_run(mock_valid_site_type, *args):
    cycle = {'cycleDuration': 365}

    # with valid siteType => not run
    mock_valid_site_type.return_value = True
    should_run, *args = _should_run(cycle)
    assert not should_run

    # no animal product => no run
    cycle['products'] = []
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with animal product => not run
    cycle['products'] = [
        {
            'term': {'termType': TermTermType.ANIMALPRODUCT.value},
            'value': [2]
        }
    ]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with matching animal => run
    cycle['animals'] = [
        {
            'term': {'termType': TermTermType.LIVEANIMAL.value, '@id': 'chicken'},
            'value': 2
        }
    ]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*argsm):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
