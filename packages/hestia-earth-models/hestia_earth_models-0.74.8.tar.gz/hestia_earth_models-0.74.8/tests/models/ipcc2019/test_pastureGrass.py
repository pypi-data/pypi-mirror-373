from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_input

from hestia_earth.models.ipcc2019.pastureGrass import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
class_path_utils = f"{class_path}_utils"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"
MILK_YIELD_TERMS = ['milkYieldPerCowRaw', 'milkYieldPerSheepRaw']
WOOL_TERMS = ['woolSheepGreasy']
TERMS_BY_ID = {
    'surinameGrassFreshForage': {
        '@id': 'surinameGrassFreshForage',
        'termType': 'forage',
        'defaultProperties': [
            {'term': {'@id': 'energyContentHigherHeatingValue'}, 'value': 4.8508},
            {'term': {'@id': 'energyDigestibilityRuminants'}, 'value': 52.7}
        ]
    },
    'alangAlangFreshForage': {
        '@id': 'alangAlangFreshForage',
        'termType': 'forage',
        'defaultProperties': [
            {'term': {'@id': 'energyContentHigherHeatingValue'}, 'value': 5.9334},
            {'term': {'@id': 'energyDigestibilityRuminants'}, 'value': 54.7}
        ]
    },
    'energyContentHigherHeatingValue': {'units': 'MJ / kg'},
    'energyDigestibilityRuminants': {'units': '%'}
}


def fake_download_hestia(term, *args):
    term_id = term.get('@id') if isinstance(term, dict) else term
    return TERMS_BY_ID.get(term_id, {})


@patch(f"{class_path_utils}.download_hestia", side_effect=fake_download_hestia)
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_hestia)
@patch(f"{class_path}.get_wool_terms", return_value=WOOL_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=MILK_YIELD_TERMS)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path_utils}.download_hestia", side_effect=fake_download_hestia)
@patch("hestia_earth.models.utils.property.download_term", side_effect=fake_download_hestia)
@patch(f"{class_path}.get_wool_terms", return_value=WOOL_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils.get_milkYield_terms", return_value=MILK_YIELD_TERMS)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run_with_goats(*args):
    with open(f"{fixtures_folder}/with-goats/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-goats/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
