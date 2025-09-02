import os
import json
import pytest
from unittest.mock import Mock, patch
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.hestia.pToSurfaceWaterAquacultureSystems import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


def _fake_download_term(term_id, *args):
    return {'@id': term_id, 'units': '%'}


@pytest.mark.parametrize(
    'test_name,cycle,expected_should_run',
    [
        (
            'incomplete => no run',
            {},
            False
        ),
        (
            'complete => run',
            {
                'completeness': {
                    'animalFeed': True,
                    'product': True,
                    'fertiliser': True,
                    'liveAnimalInput': True,
                }
            },
            True
        ),
    ]
)
def test_should_run(test_name, cycle, expected_should_run):
    should_run = _should_run(cycle)
    assert should_run == expected_should_run, test_name


@pytest.mark.parametrize('folder', _folders)
@patch('hestia_earth.models.utils.property.download_term', side_effect=_fake_download_term)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(mock_new_emission: Mock, mock_download_term: Mock, folder):
    with open(f"{fixtures_folder}/{folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected, folder
