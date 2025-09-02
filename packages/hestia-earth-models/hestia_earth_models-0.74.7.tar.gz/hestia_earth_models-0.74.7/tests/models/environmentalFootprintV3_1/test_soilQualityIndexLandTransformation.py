import json
from unittest.mock import Mock, patch

from pytest import mark

from hestia_earth.models.environmentalFootprintV3_1 import MODEL_FOLDER
from hestia_earth.models.environmentalFootprintV3_1.soilQualityIndexLandTransformation import (
    MODEL, TERM_ID, run, _should_run
)
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL_FOLDER}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL_FOLDER}/{TERM_ID}"


def fake_rounded_indicator(value: float):
    indicator = fake_new_indicator(TERM_ID, MODEL)
    indicator['value'] = round(value, 7)
    return indicator


crop_land = {"@id": "cropland", "termType": "landCover"}
sea_land_cover = {"@id": "seaOrOcean", "termType": "landCover"}
forest = {"@id": "forest", "termType": "landCover"}

indicator_inputs_production = {
    "@id": "landTransformation20YearAverageInputsProduction",
    "termType": "resourceUse",
    "units": "m2 / year"
}

indicator_during_cycle = {
    "@id": "landTransformation20YearAverageDuringCycle",
    "termType": "resourceUse",
    "units": "m2 / year"
}

wrong_indicator = {"term": {"@id": "NOT_VALID_INDICATOR_ID", "termType": "resourceUse", "units": "m2 / year"},
                   "value": 0.5, "landCover": crop_land, "previousLandCover": forest}

indicator_no_land_cover = {
    "term": indicator_during_cycle,
    "previousLandCover": forest,
    "value": 0.5}

indicator_no_previous_land_cover = {
    "term": indicator_during_cycle,
    "landCover": crop_land,
    "value": 0.5}

indicator_bad_area_value = {
    "term": indicator_during_cycle,
    "value": -10,
    "previousLandCover": forest,
    "landCover": crop_land}

indicator_zero_area_value = {
    "term": indicator_during_cycle,
    "value": 0,
    "previousLandCover": forest,
    "landCover": crop_land}

inputs_production_indicator_from_forest_to_no_cf = {
    "term": indicator_inputs_production,
    "value": 0.5,
    "previousLandCover": forest,
    "landCover": sea_land_cover}

during_cycle_indicator_from_forest_to_no_cf = {
    "term": indicator_during_cycle,
    "value": 0.5,
    "previousLandCover": forest,
    "landCover": sea_land_cover}

good_inputs_production_indicator_from_forest_to_cropland = {
    "term": indicator_inputs_production,
    "value": 0.5,
    "previousLandCover": forest,
    "landCover": crop_land}

good_inputs_production_indicator_from_forest_to_forest = {
    "term": indicator_inputs_production,
    "value": 0.5,
    "previousLandCover": forest,
    "landCover": forest}

good_during_cycle_indicator_from_forest_to_cropland = {
    "term": indicator_during_cycle,
    "value": 0.5,
    "previousLandCover": forest,
    "landCover": crop_land}

good_during_cycle_indicator_from_forest_to_forest = {
    "term": indicator_during_cycle,
    "value": 0.5,
    "previousLandCover": forest,
    "landCover": forest}


@mark.parametrize(
    "test_name, resources, expected, num_inputs",
    [
        ("No emissionsResourceUse => no run, 0 dict", [], False, 0),
        ("Wrong indicator termid => no run, 0 dict", [wrong_indicator], False, 0),
        ("Indicator no landcover terms => no run", [indicator_no_land_cover], False, 0),
        ("Indicator no previousLandCover terms => no run", [indicator_no_previous_land_cover], False, 0),
        ("Bad m2 / year area value => no run", [indicator_bad_area_value], False, 0),
        ("One good and one Bad m2 / year area value => no run", [
            good_during_cycle_indicator_from_forest_to_cropland,
            indicator_bad_area_value], False, 1),
        ("One 0 m2 / year area value => filter and run, 0 dict", [indicator_zero_area_value], True, 1),
        ("One good during cycle transformation => run, 1 dict", [good_during_cycle_indicator_from_forest_to_cropland
                                                                 ], True, 1),
        ("One 0 during cycle transformation => run, 1 dict", [good_during_cycle_indicator_from_forest_to_forest
                                                              ], True, 1),
        ("Only one good inputs production transformation => no run", [
            good_inputs_production_indicator_from_forest_to_cropland], False, 1),
        ("Good during cycle AND inputs production transformation => run, 2 dict", [
            good_during_cycle_indicator_from_forest_to_cropland,
            good_inputs_production_indicator_from_forest_to_cropland], True, 2),
        ("One 0 inputs production transformation => no run", [
            good_inputs_production_indicator_from_forest_to_forest], False, 1),
        ("Good during cycle AND inputs production 0 transformation => run, 2 dict", [
            good_during_cycle_indicator_from_forest_to_cropland,
            good_inputs_production_indicator_from_forest_to_forest], True, 2),
        ("One transformation with no CF (ocean) => run, 0 dict", [during_cycle_indicator_from_forest_to_no_cf
                                                                  ], True, 0),
        ("One good from transformation and One with no CF (ocean) => run, 1 dict", [
            good_inputs_production_indicator_from_forest_to_cropland,
            during_cycle_indicator_from_forest_to_no_cf], True, 1),
        ("Multiple good indicators => run, 2 dict", [good_inputs_production_indicator_from_forest_to_cropland,
                                                     good_during_cycle_indicator_from_forest_to_cropland], True, 2),
        ("One good, one wrong indicator => filter and run, 1 dict", [
            good_during_cycle_indicator_from_forest_to_cropland,
            wrong_indicator], True, 1),
    ]
)
def test_should_run(test_name: str, resources: list, expected: bool, num_inputs: int):
    with open(f"{fixtures_folder}/multipleTransformations/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    impact['emissionsResourceUse'] = resources

    should_run, resources_with_cf = _should_run(impact)
    assert should_run is expected
    assert len(resources_with_cf) == num_inputs


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/multipleTransformations/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/multipleTransformations/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_italy(*args):
    with open(f"{fixtures_folder}/Italy/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/Italy/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@mark.parametrize(
    "added_data",
    [
        {"country": {}},
        {"country": {"@id": "region-europe", "@type": "Term", "name": "Europe"}},
    ],
    ids=["No country/region => default to region world",
         "region-europe not in the lookup file => default to region world"]
)
@patch(f"{class_path}._indicator", side_effect=fake_rounded_indicator)
def test_run_with_country_fallback(mocked_indicator: Mock, added_data: dict):
    """
    When given valid sub-region or country not in the lookup file, default to country 'region-world' with value 574.56
    """

    with open(f"{fixtures_folder}/multipleTransformations/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    impact = impact | added_data

    value = run(impact)
    assert value['value'] == 574.56
