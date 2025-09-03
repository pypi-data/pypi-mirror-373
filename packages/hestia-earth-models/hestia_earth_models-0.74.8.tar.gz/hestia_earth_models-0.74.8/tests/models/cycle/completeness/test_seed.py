from unittest.mock import patch

from hestia_earth.models.cycle.completeness.seed import run, MODEL_KEY

class_path = f"hestia_earth.models.cycle.completeness.{MODEL_KEY}"


@patch(f"{class_path}.find_term_match", return_value=None)
def test_run_seed(mock_find_term):
    cycle = {}

    # on cropland => not complete
    cycle['site'] = {'siteType': 'cropland'}
    assert not run(cycle)

    # with input => complete
    mock_find_term.return_value = {'value': [10]}
    assert run(cycle) is True


@patch(f"{class_path}.is_plantation", return_value=False)
@patch(f"{class_path}.find_term_match", return_value=None)
def test_run_saplingsDepreciatedAmountPerCycle(mock_find_term, mock_is_plantation):
    cycle = {}

    # on cropland => not complete
    cycle['site'] = {'siteType': 'cropland'}
    assert not run(cycle)

    # with orchard crop => not complete
    mock_is_plantation.return_value = True
    assert not run(cycle)

    # with input => complete
    mock_find_term.return_value = {'value': [10]}
    assert run(cycle) is True
