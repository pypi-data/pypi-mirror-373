from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.pooreNemecek2018.excretaKgN import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.excretaKgN"
fixtures_folder = f"{fixtures_path}/{MODEL}/excretaKgN"


@patch(f"{class_path}._get_nitrogen_content", return_value=10)
@patch(f"{class_path}.convert_to_nitrogen", return_value=0)
@patch(f"{class_path}.get_animal_produced_nitrogen", return_value=0)
def test_should_run(mock_animal_produced, mock_get_feed, *args):
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # completeness False => no run
    cycle = {
        'completeness': {
            'animalFeed': False,
            'product': False
        }
    }
    mock_get_feed.return_value = 0
    mock_animal_produced.return_value = 0
    should_run, *args = _should_run(cycle)
    assert not should_run

    # completeness True => run
    cycle = {
        'completeness': {
            'animalFeed': True,
            'product': True
        }
    }
    mock_get_feed.return_value = 5
    mock_animal_produced.return_value = 5
    should_run, *args = _should_run(cycle)
    assert should_run is True

    # excreta already present with no value => run
    cycle['products'] = [
        {
            'term': {
                '@id': 'broilerChicken',
                'termType': 'liveAnimal'
            }
        },
        {
            'term': {
                '@id': 'excretaKgN',
                'termType': 'excreta'
            }
        }
    ]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch("hestia_earth.models.utils.property.download_term", return_value={'units': '%'})
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch("hestia_earth.models.utils.property.download_term", return_value={'units': '%'})
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_with_liveweight(*args):
    with open(f"{fixtures_folder}/with-liveweight/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-liveweight/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch("hestia_earth.models.utils.property.download_term", return_value={'units': '%'})
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_with_carcass(*args):
    with open(f"{fixtures_folder}/with-carcass/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-carcass/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch("hestia_earth.models.utils.property.download_term", return_value={'units': '%'})
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_with_head(*args):
    with open(f"{fixtures_folder}/with-head/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-head/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch("hestia_earth.models.utils.property.download_term", return_value={'units': '%'})
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_with_liveAquaticSpecies(*args):
    with open(f"{fixtures_folder}/with-liveAquaticSpecies/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-liveAquaticSpecies/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
