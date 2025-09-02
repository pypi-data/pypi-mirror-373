import pytest
from unittest.mock import Mock, patch
from hestia_earth.schema import SiteSiteType

from hestia_earth.models.utils.site import region_level_1_id, related_cycles, valid_site_type, get_land_cover_term_id

class_path = 'hestia_earth.models.utils.site'
CYCLE = {'@id': 'id'}


def test_region_level_1_id():
    assert region_level_1_id('GADM-ITA') == 'GADM-ITA'
    assert region_level_1_id('GADM-ITA.16_1') == 'GADM-ITA.16_1'
    assert region_level_1_id('GADM-ITA.16.10_1') == 'GADM-ITA.16_1'
    assert region_level_1_id('GADM-ITA.16.10.3_1') == 'GADM-ITA.16_1'
    assert region_level_1_id('GADM-RWA.5.3.10.4_1') == 'GADM-RWA.5_1'
    assert region_level_1_id('GADM-RWA.5.3.10.4.3_1') == 'GADM-RWA.5_1'

    assert not region_level_1_id('region-world')


@patch(f"{class_path}.find_related", return_value=[CYCLE])
@patch(f"{class_path}._load_calculated_node", return_value=CYCLE)
def test_related_cycles(*args):
    assert related_cycles({'@id': 'id'}) == [CYCLE]


@patch(f"{class_path}.find_related", return_value=[CYCLE])
@patch(f"{class_path}._load_calculated_node")
def test_related_cycles_with_mapping(_load_calculated_node_mock, find_related_mock):
    assert related_cycles({'@id': 'id'}, {'id': CYCLE}) == [CYCLE]
    _load_calculated_node_mock.assert_not_called()  # Confirm the load function is not used for nodes in mapping


def test_valid_site_type():
    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert valid_site_type(site) is True

    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert not valid_site_type(site, [SiteSiteType.OTHER_NATURAL_VEGETATION.value])


_LAND_COVER_TERMS = [
    {'@type': 'Term', 'name': 'Glass or high accessible cover', '@id': 'glassOrHighAccessibleCover'},
    {'@type': 'Term', 'name': 'Sea or ocean', '@id': 'seaOrOcean'},
    {'@type': 'Term', 'name': 'River or stream', '@id': 'riverOrStream'},
    {'@type': 'Term', 'name': 'Other natural vegetation', '@id': 'otherNaturalVegetation'},
    {'@type': 'Term', 'name': 'Food retailer', '@id': 'foodRetailer'},
    {'@type': 'Term', 'name': 'Agri-food processor', '@id': 'agriFoodProcessor'},
    {'@type': 'Term', 'name': 'Permanent pasture', '@id': 'permanentPasture'},
    {'@type': 'Term', 'name': 'Animal housing', '@id': 'animalHousing'},
    {'@type': 'Term', 'name': 'Forest', '@id': 'forest'},
    {'@type': 'Term', 'name': 'Lake', '@id': 'lake'},
    {'@type': 'Term', 'name': 'Pond', '@id': 'pond'},
    {'@type': 'Term', 'name': 'Cropland', '@id': 'cropland'},
]


@pytest.mark.parametrize(
    'site_type,expected_landCover_id',
    [
        (SiteSiteType.CROPLAND.value, 'cropland'),
        (SiteSiteType.SEA_OR_OCEAN.value, 'seaOrOcean'),
        (SiteSiteType.AGRI_FOOD_PROCESSOR.value, 'agriFoodProcessor'),
        (SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value, 'glassOrHighAccessibleCover'),
    ]
)
@patch(f"{class_path}.get_land_cover_siteTypes", return_value=_LAND_COVER_TERMS)
def test_get_land_cover_term_id(mock_terms: Mock, site_type: str, expected_landCover_id: str):
    assert get_land_cover_term_id(site_type) == expected_landCover_id, site_type
