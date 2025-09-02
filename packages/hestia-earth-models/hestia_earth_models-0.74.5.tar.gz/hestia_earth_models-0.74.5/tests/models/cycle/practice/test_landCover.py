import os
import json
import pytest
from unittest.mock import Mock, patch

from tests.utils import fixtures_path, fake_new_practice
from hestia_earth.models.cycle.practice.landCover import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.practice.{MODEL_KEY}"
fixtures_folder = os.path.join(fixtures_path, MODEL, 'practice', MODEL_KEY)

_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


@pytest.mark.parametrize('folder', _folders)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(mock_new_practice: Mock, folder: str):
    fixture_path = os.path.join(fixtures_folder, folder)

    with open(f"{fixture_path}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixture_path}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected, fixture_path
