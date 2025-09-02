import pytest

from hestia_earth.models.site.pre_checks.cache_geospatialDatabase import list_rasters, list_vectors


def test_list_rasters():
    rasters = list_rasters(years=[2010])
    assert len(rasters) == 73


@pytest.mark.parametrize(
    'name,site,expected_len',
    [
        ('without values', {}, 4),
        ('with region', {'region': 'region'}, 3),
        ('with ecoregion', {'ecoregion': 'ecoregion'}, 3),
        ('with awareWaterBasinId', {'awareWaterBasinId': 'awareWaterBasinId'}, 3),
    ]
)
def test_list_vectors(name: str, site: dict, expected_len: int):
    vectors = list_vectors([site])
    assert len(vectors) == expected_len, name
