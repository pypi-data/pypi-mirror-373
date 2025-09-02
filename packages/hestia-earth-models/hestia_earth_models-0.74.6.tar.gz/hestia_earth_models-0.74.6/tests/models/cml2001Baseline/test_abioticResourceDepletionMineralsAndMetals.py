import json
from unittest.mock import patch

from pytest import mark

from hestia_earth.models.cml2001Baseline.abioticResourceDepletionMineralsAndMetals import MODEL, TERM_ID, run, \
    _should_run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def fake_rounded_indicator(value: float):
    indicator = fake_new_indicator(TERM_ID, MODEL)
    indicator['value'] = round(value, 7)
    return indicator


iodine_input = {"@id": "iodineMaterial", "termType": "material", "units": "kg"}
boron_input = {"@id": "boron", "termType": "soilAmendment", "units": "kg B"}
tellurium_input = {"@id": "CAS-13494-80-9", "termType": "otherInorganicChemical", "units": "kg"}
input_no_cf_material = {"@id": "cork", "termType": "material", "units": "kg"}

wrong_indicator = {'value': [1],
                   'term': {'@id': 'landTransformation20YearAverageDuringCycle', 'termType': 'resourceUse'},
                   'inputs': [iodine_input]}

indicator_no_inputs = {'value': 3,
                       'term': {'@id': 'resourceUseMineralsAndMetalsInputsProduction', 'termType': 'resourceUse'},
                       'inputs': []}
indicator_2_inputs = {
    'value': 3, 'term': {'@id': 'resourceUseMineralsAndMetalsInputsProduction', 'termType': 'resourceUse'},
    'inputs': [boron_input, iodine_input]
}

indicator_no_unit = {
    'value': 3, 'term': {'@id': 'resourceUseMineralsAndMetalsInputsProduction', 'termType': 'resourceUse'},
    'inputs': [{"@id": "iodineMaterial", "termType": "material", }],
}

indicator_wrong_unit = {
    'value': 3, 'term': {'@id': 'resourceUseMineralsAndMetalsInputsProduction', 'termType': 'resourceUse'},
    'inputs': [{"@id": "iodineMaterial", "termType": "material", "units": "Mj"}],
}

indicator_no_cf_material = {
    'value': 3, 'term': {'@id': 'resourceUseMineralsAndMetalsInputsProduction', 'termType': 'resourceUse'},
    'inputs': [input_no_cf_material]
}

indicator_iodine = {
    'value': [1],
    'term': {'@id': 'resourceUseMineralsAndMetalsInputsProduction', 'termType': 'resourceUse'},
    'inputs': [iodine_input]
}

indicator_boron = {
    'value': 2,
    'term': {'@id': 'resourceUseMineralsAndMetalsInputsProduction', 'termType': 'resourceUse'},
    'inputs': [boron_input]
}

indicator_tellurium = {
    'value': 2,
    'term': {'@id': 'resourceUseMineralsAndMetalsInputsProduction', 'termType': 'resourceUse'},
    'inputs': [tellurium_input]
}


@mark.parametrize(
    "resources, expected, num_inputs",
    [
        ([], False, 0),
        ([wrong_indicator], False, 0),
        ([indicator_no_inputs], False, 0),
        ([indicator_2_inputs], False, 0),
        ([indicator_no_unit], False, 0),
        ([indicator_wrong_unit], False, 0),
        ([indicator_no_cf_material], True, 0),
        ([indicator_iodine], True, 1),
        ([indicator_boron], True, 1),
        ([indicator_tellurium], True, 1),
        ([indicator_iodine, indicator_no_cf_material], True, 1),
    ],
    ids=["No indicators", "wrong indicator", "indicator no inputs", "indicator 2 inputs", "missing unit", "wrong unit",
         "material with no cf", "good input material", "good input soilAmendment", "good input otherInorganicChemical",
         "one good input"]
)
def test_should_run(resources, expected, num_inputs):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    impactassessment['emissionsResourceUse'] = resources

    should_run, grouped_inputs = _should_run(impactassessment)
    assert should_run is expected
    assert len(grouped_inputs) == num_inputs


@patch(f"{class_path}._indicator", side_effect=fake_rounded_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impactassessment)
    assert value == expected
