from hestia_earth.models.utils import current_date, max_date


def test_max_date():
    assert max_date('2100-01-01') == current_date()
    assert max_date('2000-01-01') == '2000-01-01'
