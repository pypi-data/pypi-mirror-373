import os
import json
import pytest
from unittest.mock import MagicMock, patch
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.hestia.histosol import MODEL, TERM_ID, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


@pytest.mark.parametrize("folder", _folders)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(mock_new_measurement: MagicMock, folder: str):
    with open(f"{fixtures_folder}/{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(site)
    assert value == expected, folder
