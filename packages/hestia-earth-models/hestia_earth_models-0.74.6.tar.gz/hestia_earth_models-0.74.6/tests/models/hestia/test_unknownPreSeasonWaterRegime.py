from unittest.mock import patch
import json
from tests.utils import fake_new_practice, fixtures_path

from hestia_earth.models.hestia.unknownPreSeasonWaterRegime import MODEL, TERM_ID, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

_PRACTICE_TERM_ID = 'nonFloodedPreSeasonLessThan180Days'


@patch(f"{class_path}.get_flooded_pre_season_terms", return_value=[_PRACTICE_TERM_ID])
def test_should_run(*args):
    # with the practice => no run
    cycle = {'practices': [{'term': {'@id': _PRACTICE_TERM_ID}}]}
    should_run = _should_run(cycle)
    assert not should_run

    # without the practice => run
    cycle = {'practices': []}
    should_run = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}.get_flooded_pre_season_terms", return_value=[_PRACTICE_TERM_ID])
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(data)
    assert result == expected
