from unittest.mock import patch
import pytest

from hestia_earth.models.data.hestiaAggregatedData import find_closest_impact_id

class_path = 'hestia_earth.models.data.hestiaAggregatedData'

product_id = 'productId'
country_id = 'countryId'
fake_data = {
    product_id: {
        country_id: {
            '2025': 'id-2025',
            '2009': 'id-2009',
            '1990': 'id-1990'
        }
    }
}


@pytest.mark.parametrize(
    'year,expected',
    [
        (2030, 'id-2025'),
        (2019, 'id-2009'),
        (2001, 'id-1990'),
        (1969, None),
    ]
)
@patch(f"{class_path}._get_data", return_value=fake_data)
def test_find_closest_impact_id(mock_get_data, year: int, expected):
    assert find_closest_impact_id(product_id, country_id, year) == expected, year
