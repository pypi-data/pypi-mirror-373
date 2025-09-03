import pytest
from hestia_earth.schema import SiteSiteType, TermTermType

from hestia_earth.models.utils.crop import valid_site_type, get_landCover_term_id

class_path = 'hestia_earth.models.utils.crop'


def test_valid_site_type():
    site = {'siteType': SiteSiteType.CROPLAND.value}
    cycle = {'site': site}
    assert valid_site_type(cycle) is True

    cycle['site']['siteType'] = SiteSiteType.PERMANENT_PASTURE.value
    assert not valid_site_type(cycle)
    assert not valid_site_type(site, True) is True


@pytest.mark.parametrize(
    'term,expected',
    [
        ({'termType': TermTermType.CROP.value, '@id': 'wheatGrain'}, 'wheatPlant'),
        ({'termType': TermTermType.SEED.value, '@id': 'saplings'}, None),
    ]
)
def test_get_landCover_term_id(term: dict, expected: str):
    assert get_landCover_term_id(term) == expected, term.get('@id')
