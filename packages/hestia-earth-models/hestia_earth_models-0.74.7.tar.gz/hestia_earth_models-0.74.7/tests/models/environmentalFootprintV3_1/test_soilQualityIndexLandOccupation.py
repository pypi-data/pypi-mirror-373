import json
from unittest.mock import patch

import pytest

from hestia_earth.models.environmentalFootprintV3_1 import MODEL_FOLDER
from hestia_earth.models.environmentalFootprintV3_1.soilQualityIndexLandOccupation import TERM_ID, run, \
    _should_run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL_FOLDER}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL_FOLDER}/{TERM_ID}"

crop_land = {"@id": "cropland", "termType": "landCover"}
sea_land_cover = {"@id": "seaOrOcean", "termType": "landCover"}
forest = {"@id": "forest", "termType": "landCover"}

wrong_indicator = {"term": {"@id": "NOT_landOccupationInputsProduction", "termType": "resourceUse", "units": "m2*year"},
                   "value": 0.5, "landCover": crop_land}

indicator_no_land_cover = {
    "term": {"@id": "landOccupationInputsProduction", "termType": "resourceUse", "units": "m2*year"},
    "value": 0.5}

indicator_no_unit = {"term": {"@id": "landOccupationInputsProduction", "termType": "resourceUse"},
                     "value": 0.5, "landCover": crop_land}

indicator_wrong_unit = {
    "term": {"@id": "landOccupationInputsProduction", "termType": "resourceUse", "units": "ha*day"}, "value": 0.5,
    "landCover": crop_land}

indicator_value_0 = {
    "term": {"@id": "landOccupationInputsProduction", "termType": "resourceUse", "units": "m2*year"}, "value": 0,
    "landCover": crop_land}

inputs_production_indicator_no_cf = {
    "term": {"@id": "landOccupationInputsProduction", "termType": "resourceUse", "units": "m2*year"}, "value": 0.5,
    "landCover": sea_land_cover}

good_inputs_production_indicator_cropland = {
    "term": {"@id": "landOccupationInputsProduction", "termType": "resourceUse", "units": "m2*year"}, "value": 0.5,
    "landCover": crop_land}

good_inputs_production_indicator_forest = {
    "term": {"@id": "landOccupationInputsProduction", "termType": "resourceUse", "units": "m2*year"}, "value": 0.5,
    "landCover": forest}

good_during_cycle_indicator_cropland = {
    "term": {"@id": "landOccupationDuringCycle", "termType": "resourceUse", "units": "m2*year"}, "value": 0.5,
    "landCover": crop_land}

good_during_cycle_indicator_forest = {
    "term": {"@id": "landOccupationDuringCycle", "termType": "resourceUse", "units": "m2*year"}, "value": 0.5,
    "landCover": forest}


@pytest.mark.parametrize(
    "resources, expected, num_inputs",
    [
        ([], False, 0),
        ([wrong_indicator], False, 0),
        ([indicator_no_land_cover], False, 0),
        ([indicator_no_unit], False, 0),
        ([indicator_wrong_unit], False, 0),
        ([indicator_value_0], True, 1),
        ([inputs_production_indicator_no_cf], True, 0),
        ([good_during_cycle_indicator_cropland], True, 1),
        ([good_during_cycle_indicator_cropland, good_inputs_production_indicator_forest], True, 2),
        ([good_during_cycle_indicator_cropland, inputs_production_indicator_no_cf], True, 1),
        ([good_during_cycle_indicator_cropland, good_during_cycle_indicator_forest,
          good_inputs_production_indicator_forest, good_inputs_production_indicator_cropland], True, 4),

    ],
    ids=["No emissionsResourceUse => no run",
         "Wrong indicator termid => no run",
         "Indicator no landcover terms => no run",
         "Missing unit => no run",
         "Wrong unit => no run",
         "With 0 value => run",
         "Input with no cf => run, empty input",
         "One good input => run, 1 dict",
         "Two good input => run, 2 dict",
         "One good input and One with no CF => run, 2 dict",
         "Multiple good indicators with same id => run, 4 dict",
         ]
)
def test_should_run(resources, expected, num_inputs):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    impactassessment['emissionsResourceUse'] = resources

    should_run, resources_with_cf = _should_run(impactassessment)
    assert should_run is expected
    assert len(resources_with_cf) == num_inputs


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_with_subclass_landcover(*args):
    """
    Example data:
    Country: Italy
    Quantity in m2*year: 1
    CF METHOD factor: 50.438

    landCover field "plantationForest" should map to
    Name Flow: "forest, intensive Land occupation"
    """

    with open(f"{fixtures_folder}/plantationForest/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)
    with open(f"{fixtures_folder}/plantationForest/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_with_region_missing_data(*args):
    """
    When given valid sub-region or country not in the lookup file should default to 'region-world'
    """
    with open(f"{fixtures_folder}/default-region-world/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/default-region-world/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_with_no_region(*args):
    """
    When no location is specified, defaults to region world.
    """
    with open(f"{fixtures_folder}/default-region-world/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    del impact['country']

    with open(f"{fixtures_folder}/default-region-world/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
