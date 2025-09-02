from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019.nh3ToAirInorganicFertiliser import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._is_term_type_complete", return_value=False)
@patch(f"{class_path}.get_inorganic_fertiliser_N_total", return_value=0)
def test_should_run(mock_N_total, mock_complete, *args):
    # no N => no run
    assert not _should_run({})

    # with N => no run
    mock_N_total.return_value = 10
    assert not _should_run({})

    # is complete => run
    mock_complete.return_value = True
    assert _should_run({}) is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_aggregated(*args):
    with open(f"{fixtures_folder}/aggregated/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/aggregated/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_disaggregated(*args):
    with open(f"{fixtures_folder}/disaggregated/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/disaggregated/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
