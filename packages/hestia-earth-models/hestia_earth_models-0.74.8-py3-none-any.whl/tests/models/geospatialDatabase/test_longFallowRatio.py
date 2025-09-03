from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.geospatialDatabase.longFallowRatio import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.is_plantation")
def test_should_run(mock_is_plantation, *args):
    cycle = {'@type': 'Cycle'}

    mock_is_plantation.return_value = False
    should_run = _should_run(cycle)
    assert should_run is True

    mock_is_plantation.return_value = True
    should_run = _should_run(cycle)
    assert not should_run


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
