import os
import json
import pytest
from unittest.mock import patch, Mock
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.hestia.seed_emissions import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = os.path.join(fixtures_path, MODEL, MODEL_KEY)

_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


@pytest.mark.parametrize('folder', _folders)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(mock_emission: Mock, folder: str):
    fixture_path = os.path.join(fixtures_folder, folder)

    with open(f"{fixture_path}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixture_path}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected, folder
