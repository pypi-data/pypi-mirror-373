import json
from unittest.mock import patch

import pytest

from hestia_earth.models.frischknechtEtAl2000.ionisingRadiationKbqU235Eq import MODEL, TERM_ID, run, _should_run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

hydrogen3_input = {"@id": "hydrogen3", "termType": "waste", "units": "kg"}
cesium134_input = {"@id": "cesium134", "termType": "waste", "units": "kg"}
cesium137_input = {"@id": "cesium137", "termType": "waste", "units": "kg"}
uranium234_input = {"@id": "uranium234", "termType": "waste", "units": "kg"}
iodine129_input = {"@id": "iodine129", "termType": "waste", "units": "kg"}
no_cf_input = {"@id": "oilPalmMillEffluentWaste", "termType": "waste", "units": "kg"}

wrong_indicator = {
    "term": {
        "@id": "co2ToAirSoilOrganicCarbonStockChangeManagementChange",
        "termType": "emission",
    },
    "value": 3,
    "key": hydrogen3_input
}

indicator_no_key = {
    "term": {"@id": "ionisingCompoundsToAirInputsProduction", "termType": "emission"},
    "value": 3
}

indicator_no_unit = {
    "term": {"@id": "ionisingCompoundsToAirInputsProduction", "termType": "emission"},
    "value": 3,
    "key": {"@id": "hydrogen3", "termType": "waste"}
}

indicator_wrong_unit = {
    "term": {"@id": "ionisingCompoundsToAirInputsProduction", "termType": "emission"},
    "value": 3,
    "key": {"@id": "hydrogen3", "termType": "waste", "units": "not_a_unit"}
}

indicator_no_cf_input = {
    "term": {"@id": "ionisingCompoundsToAirInputsProduction", "termType": "emission"},
    "value": 3,
    "key": no_cf_input
}

indicator_hydrogen3_input = {
    "term": {"@id": "ionisingCompoundsToAirInputsProduction", "termType": "emission"},
    "value": 3,
    "key": hydrogen3_input
}

indicator_cesium137_water = {
    "term": {"@id": "ionisingCompoundsToWaterInputsProduction", "termType": "emission"},
    "value": 3,
    "key": cesium137_input
}

indicator_cesium137_air = {
    "term": {"@id": "ionisingCompoundsToAirInputsProduction", "termType": "emission"},
    "value": 3,
    "key": cesium137_input
}

indicator_cesium137_salt_water = {
    "term": {
        "@id": "ionisingCompoundsToSaltwaterInputsProduction",
        "termType": "emission",
    },
    "value": 3,
    "key": cesium137_input
}

indicator_uranium234_input = {
    "term": {
        "@id": "ionisingCompoundsToSaltwaterInputsProduction",
        "termType": "emission",
    },
    "value": 3,
    "key": uranium234_input
}


@pytest.mark.parametrize(
    "resources, expected, num_key",
    [
        ([], False, 0),
        ([wrong_indicator], False, 0),
        ([indicator_no_key], False, 0),
        ([indicator_no_unit], False, 0),
        ([indicator_wrong_unit], False, 0),
        ([indicator_no_cf_input], True, 0),
        ([indicator_hydrogen3_input], True, 1),
        ([indicator_cesium137_water], True, 1),
        ([indicator_uranium234_input], True, 1),
        ([indicator_cesium137_water, indicator_no_cf_input], True, 1),
        ([indicator_cesium137_water, indicator_cesium137_water], True, 2),
        ([indicator_cesium137_water, indicator_cesium137_salt_water, indicator_cesium137_air], True, 3),
    ],
    ids=["No emissionsResourceUse => run, empty input",
         "Wrong indicator termid => run, empty input",
         "Indicator no key => no run",
         "Missing unit => no run",
         "Wrong unit => no run",
         "Input with no cf => run, empty input",
         "Good input ionisingCompoundsToAirInputsProduction => run, 1 input",
         "Good input ionisingCompoundsToWaterInputsProduction => run, 1 input",
         "Good input ionisingCompoundsToSaltwaterInputsProduction => run, 1 input",
         "One good input => run, 1 input",
         "2 identical indicators => run 2 input",
         "3 different indicators common input => run 3 input",
         ]
)
def test_should_run(resources, expected, num_key):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    impactassessment['emissionsResourceUse'] = resources

    should_run, resources_with_cf = _should_run(impactassessment)
    assert should_run is expected
    assert len(resources_with_cf) == num_key


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impactassessment)
    assert value == expected
