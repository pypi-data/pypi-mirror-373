from unittest.mock import patch

from hestia_earth.models.site.pre_checks.cache_years import CACHE_KEY, CACHE_YEARS_KEY, run, _should_run

class_path = 'hestia_earth.models.site.pre_checks.cache_years'
years = [2019, 2020]


@patch(f"{class_path}.related_years")
def test_should_run(mock_related_years):
    # no related years => no run
    mock_related_years.return_value = []
    should_run, *args = _should_run({})
    assert not should_run

    # with related years => run
    mock_related_years.return_value = years
    should_run, *args = _should_run({})
    assert should_run is True


@patch(f"{class_path}.related_years", return_value=years)
def test_run(*args):
    result = run({})
    assert result.get(CACHE_KEY).get(CACHE_YEARS_KEY) == years
