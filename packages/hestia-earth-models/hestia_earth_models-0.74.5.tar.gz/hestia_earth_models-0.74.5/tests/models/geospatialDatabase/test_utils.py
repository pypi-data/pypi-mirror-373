import json
from unittest.mock import patch
from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path

from hestia_earth.models.geospatialDatabase import MODEL
from hestia_earth.models.geospatialDatabase.utils import get_region_factor, get_area_size, _get_boundary_area_size

class_path = 'hestia_earth.models.geospatialDatabase.utils'
fixtures_folder = f"{fixtures_path}/{MODEL}/utils"

AREA = 1000
COUNTRY = {
    '@id': 'GADM-ALB',
    'area': AREA
}


def test_get_region_factor():
    site = {'country': COUNTRY}
    value = get_region_factor('croppingIntensity', site, TermTermType.LANDUSEMANAGEMENT)
    assert round(value, 5) == 0.99998


@patch(f"{class_path}.download_term", return_value={'area': AREA})
def test_get_area_size(*args):
    site = {'country': COUNTRY}
    assert get_area_size(site) == AREA

    site['boundary'] = {'type': 'Polygon'}
    site['boundaryArea'] = AREA
    assert get_area_size(site) == AREA


def test_get_boundary_area_size():
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    assert _get_boundary_area_size(boundary=site.get('boundary')) == 4896.1559583013795
