from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.hestia.concentrateFeed import MODEL, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.concentrateFeed"
fixtures_folder = f"{fixtures_path}/{MODEL}/concentrateFeed"

DE_TERM_IDS = [
    'digestibleEnergySalmonids', 'digestibleEnergyRuminants', 'digestibleEnergyPoultry',
    'digestibleEnergyPigs', 'digestibleEnergyRabbits', 'digestibleEnergyOtherAnimals',
    'digestibleEnergyAquaticSpecies'
]
ED_TERM_IDS = [
    'energyDigestibilityPoultry', 'energyDigestibilityRabbits', 'energyDigestibilityPigs',
    'energyDigestibilityRuminants', 'energyDigestibilitySalmonids', 'energyDigestibilityOtherAnimals',
    'energyDigestibilityAquaticSpecies'
]


@patch(f"{class_path}.find_primary_product", return_value={})
def test_should_run(mock_primary_product, *args):
    # no primary product => no run
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with primary product => no run
    mock_primary_product.return_value = {'term': {'@id': 'concentrateFeedBlend'}}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with crop/animal product inputs => run
    cycle['inputs'] = [{'term': {'termType': 'crop'}}]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch('hestia_earth.models.utils.property.download_term', return_value={})  # make sure default props are not loaded
@patch(f"{class_path}.get_energy_digestibility_terms", return_value=ED_TERM_IDS)
@patch(f"{class_path}.get_digestible_energy_terms", return_value=DE_TERM_IDS)
@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(data)
    assert value == expected
