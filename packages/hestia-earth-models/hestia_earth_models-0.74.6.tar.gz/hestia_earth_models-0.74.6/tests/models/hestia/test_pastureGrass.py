from unittest.mock import patch
import json
from tests.utils import fake_new_practice, fixtures_path

from hestia_earth.models.hestia.pastureGrass import MODEL, TERM_ID, KEY_TERM_ID, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    # not permanent pasture => no run
    cycle = {'site': {'siteType': 'cropland'}}
    assert not _should_run(cycle)

    # permanent pasture => run
    cycle = {'site': {'siteType': 'permanent pasture'}}
    assert _should_run(cycle) is True


@patch(f"{class_path}.download_term", return_value={'@type': 'Term', '@id': KEY_TERM_ID})
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(data)
    assert result == expected
