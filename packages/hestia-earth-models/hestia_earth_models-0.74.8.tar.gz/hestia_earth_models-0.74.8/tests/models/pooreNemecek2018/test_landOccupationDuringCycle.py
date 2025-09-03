from unittest.mock import patch
import json
from hestia_earth.schema import CycleFunctionalUnit
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.pooreNemecek2018.landOccupationDuringCycle import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.get_landCover_term_id_from_site_type", return_value='cropland')
@patch(f"{class_path}.get_landCover_term_id", return_value='cropland')
@patch(f"{class_path}.land_occupation_per_kg", return_value=None)
def test_should_run(mock_land_occupation, *args):
    # with a cycle and functionalUnit = 1 ha => no run
    impact = {'cycle': {'functionalUnit': CycleFunctionalUnit._1_HA.value}}
    should_run, *args = _should_run(impact)
    assert not should_run

    # with product value and economicValueShare => run
    impact['product'] = {'economicValueShare': 10}
    mock_land_occupation.return_value = 10
    should_run, *args = _should_run(impact)
    assert should_run is True


@patch(f"{class_path}.get_landCover_term_id_from_site_type", return_value='cropland')
@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}.get_landCover_term_id_from_site_type", return_value='cropland')
@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_with_plantation(*args):
    with open(f"{fixtures_folder}/with-orchard-crop/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/with-orchard-crop/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
