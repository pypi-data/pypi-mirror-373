from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2006.n2OToAirCropResidueDecompositionDirect import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.has_flooded_rice", return_value=False)
@patch(f"{class_path}._is_term_type_complete", return_value=False)
@patch(f"{class_path}.get_crop_residue_decomposition_N_total", return_value=0)
def test_should_run(mock_N_total, mock_complete, *args):
    # no N => no run
    should_run, *args = _should_run({})
    assert not should_run

    # with N => no run
    mock_N_total.return_value = 10
    should_run, *args = _should_run({})
    assert not should_run

    # is complete => run
    mock_complete.return_value = True
    should_run, *args = _should_run({})
    assert should_run is True


@patch(f"{class_path}.has_flooded_rice", return_value=False)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.has_flooded_rice", return_value=True)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_flooded_rice(*args):
    with open(f"{fixtures_folder}/with-flooded-rice/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-flooded-rice/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
