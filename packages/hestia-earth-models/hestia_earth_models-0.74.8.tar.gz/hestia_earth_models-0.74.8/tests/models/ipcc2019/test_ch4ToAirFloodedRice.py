import os
import pytest
from unittest.mock import Mock, patch
import json
from tests.utils import fixtures_path, fake_new_emission, FLOODED_RICE_TERMS

from hestia_earth.models.ipcc2019.ch4ToAirFloodedRice import MODEL, TERM_ID, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


@pytest.mark.parametrize("folder", _folders)
@patch('hestia_earth.models.utils.product.get_rice_paddy_terms', return_value=FLOODED_RICE_TERMS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(mock_new_emission: Mock, mock_rice_terms: Mock, folder: str):
    with open(f"{fixtures_folder}/{folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/{folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected, folder
