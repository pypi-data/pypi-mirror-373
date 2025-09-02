import os
import json
import pytest
from unittest.mock import patch

from tests.utils import fixtures_path, fake_new_indicator
from hestia_earth.models.hestia.default_resourceUse import MODEL, MODEL_KEY, run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


def fake_new_indicator_extended(*args):
    data = fake_new_indicator(*args)
    data['term']['termType'] = 'resourceUse'
    return data


@pytest.mark.parametrize("subfolder", _folders)
@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator_extended)
def test_run(mock, subfolder: str):
    folder = f"{fixtures_folder}/{subfolder}"
    with open(f"{folder}/impact.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(impact)
    print(json.dumps(result, indent=2))
    assert result == expected
