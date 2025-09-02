import os
import json
import pytest
from unittest.mock import Mock, patch
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.resourceUseNotRelevant import MODEL, run

class_path = f"hestia_earth.models.{MODEL}"
fixtures_folder = f"{fixtures_path}/{MODEL}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


@pytest.mark.parametrize('folder', _folders)
@patch(f"{class_path}.get_land_cover_term_id")
@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_forest(mock_new_indicator: Mock, mock_land_cover: Mock, folder: str):
    mock_land_cover.return_value = folder

    with open(f"{fixtures_folder}/{folder}/impact.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run('all', impact)
    assert result == expected, folder
