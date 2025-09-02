from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.hestia.cationExchangeCapacityPerKgSoil import (
    MODEL, TERM_ID, run, _should_run_measurements
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.find_term_match")
def test_should_run_measurements(mock_find):
    # no measurement => no run
    mock_find.return_value = None
    assert not _should_run_measurements({}, [])

    # with measurement => run
    mock_find.return_value = {'value': [10]}
    assert _should_run_measurements({}, []) is True


@patch(f"{class_path}.get_source", return_value={})
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(*args):
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(site)
    assert value == expected
