import os
import json
import pytest
from unittest.mock import Mock, patch
from hestia_earth.schema import SiteSiteType

from tests.utils import fixtures_path, fake_new_management
from hestia_earth.models.hestia.management import MODEL, MODEL_KEY, run, _is_cover_crop, \
    _cycle_has_existing_non_cover_land_cover_nodes

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = os.path.join(fixtures_path, MODEL, MODEL_KEY)

_LAND_COVER_TERM_BY_SITE_TYPE = {
    SiteSiteType.ANIMAL_HOUSING.value: "animalHousing",
    SiteSiteType.CROPLAND.value: "cropland",
    SiteSiteType.AGRI_FOOD_PROCESSOR.value: "agriFoodProcessor",
    SiteSiteType.PERMANENT_PASTURE.value: "permanentPasture"
}
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]


@pytest.mark.parametrize(
    'term_id,expected_result',
    [
        ("coverCrop", True),
        ("catchCrop", True),
        ("groundCover", True),
        ("salinity", False),
        ("nonexistentthing", False),
    ]
)
def test_is_cover_crop(term_id, expected_result):
    assert _is_cover_crop(term_id) == expected_result


def test_cycle_has_existing_non_cover_land_cover_nodes():
    fixture_path = os.path.join(fixtures_folder, "example7")
    with open(f"{fixture_path}/cycles.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)

    assert _cycle_has_existing_non_cover_land_cover_nodes(cycles[0]) is False

    fixture_path = os.path.join(fixtures_folder, "siteType_no_cropland")
    with open(f"{fixture_path}/cycles.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)
    assert _cycle_has_existing_non_cover_land_cover_nodes(cycles[0]) is True


@pytest.mark.parametrize('folder', _folders)
@patch(
    f"{class_path}.get_landCover_term_id_from_site_type",
    side_effect=lambda site_type: _LAND_COVER_TERM_BY_SITE_TYPE[site_type]
)
@patch(f"{class_path}._new_management", side_effect=fake_new_management)
@patch(f"{class_path}.related_cycles")
def test_run(
    mock_related_cycles: Mock,
    mock_new_management: Mock,
    mock_land_cover_lookup: Mock,
    folder: str
):
    fixture_path = os.path.join(fixtures_folder, folder)

    with open(f"{fixture_path}/cycles.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)
    mock_related_cycles.return_value = cycles

    try:
        with open(f"{fixture_path}/site.jsonld", encoding='utf-8') as f:
            site = json.load(f)
    except FileNotFoundError:
        with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
            site = json.load(f)

    with open(f"{fixture_path}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected, fixture_path
