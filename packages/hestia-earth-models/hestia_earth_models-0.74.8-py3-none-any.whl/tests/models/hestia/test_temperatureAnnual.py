from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.hestia.temperatureAnnual import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    # no measuremrent => no run
    site = {'measurements': []}
    should_run, *args = _should_run(site)
    assert not should_run

    # with measuremrent => run
    site = {'measurements': [{'term': {'@id': 'temperatureMonthly'}}]}
    should_run, *args = _should_run(site)
    assert should_run is True


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(*args):
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(site)
    assert value == expected
