import json
from unittest.mock import patch

from pytest import mark

from hestia_earth.models.cml2001Baseline.abioticResourceDepletionFossilFuels import MODEL, TERM_ID, run, _should_run, \
    get_all_non_renewable_terms
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def fake_rounded_indicator(value: float):
    indicator = fake_new_indicator(TERM_ID, MODEL)
    indicator['value'] = round(value, 7)
    return indicator


def fake_get_terms(filename, column_name):
    data = {
        'fuel.csv': ["lignite", "conventionalCrudeOil", "naturalGas", "coalTar"],
        'electricity.csv': ['electricityGridMarketMix', 'electricityGridHardCoal', 'electricityProducedOnSiteHardCoal',
                            'electricityGridNaturalGas', 'electricityProducedOnSiteNaturalGas', 'electricityGridOil',
                            'electricityProducedOnSiteOil', 'electricityGridNuclear']}
    return data[filename]


input_lignite_mj = {"@id": "lignite", "name": "lignite (Brown coal)", "termType": "fuel", "units": "MJ"}

input_nuclear_fuel_mj = {"@id": "electricityGridNuclear", "name": "Any depleted nuclear fuel",
                         "termType": "electricity", "units": "MJ"}

input_excessIndustrialHeat_mj = {"@id": "excessIndustrialHeat", "name": "Excess industrial heat", "termType": "fuel",
                                 "units": "MJ"}

wrong_indicator = {"term": {"@id": "BAD_INDICATOR_ID", "termType": "resourceUse", "units": "MJ"},
                   "value": 5,
                   "inputs": [input_lignite_mj]}

indicator_no_inputs = {
    "term": {"@id": "resourceUseEnergyDepletionInputsProduction", "termType": "resourceUse", "units": "MJ"},
    "value": 5,
    "inputs": []}

indicator_2_inputs = {
    "term": {"@id": "resourceUseEnergyDepletionInputsProduction", "termType": "resourceUse", "units": "MJ"},
    "value": 5,
    "inputs": [input_lignite_mj, input_lignite_mj]}

indicator_no_unit = {"term": {"@id": "resourceUseEnergyDepletionInputsProduction", "termType": "resourceUse"},
                     "value": 5,
                     "inputs": [input_lignite_mj]}

indicator_wrong_unit = {"term": {"@id": "resourceUseEnergyDepletionInputsProduction", "termType": "resourceUse",
                                 "units": "ha"},
                        "value": 5,
                        "inputs": [input_lignite_mj]}

indicator_bad_input_id = {
    "term": {"@id": "resourceUseEnergyDepletionInputsProduction", "termType": "resourceUse", "units": "MJ"},
    "value": 5,
    "inputs": [input_excessIndustrialHeat_mj]}

good_indicator_inputs_production_mj = {
    "term": {"@id": "resourceUseEnergyDepletionInputsProduction", "termType": "resourceUse", "units": "MJ"},
    "value": 5,
    "inputs": [input_lignite_mj]
}

good_indicator_during_cycle_mj = {
    "term": {"@id": "resourceUseEnergyDepletionDuringCycle", "termType": "resourceUse", "units": "MJ"},
    "value": 5,
    "inputs": [input_lignite_mj]}

good_nuclear_indicator_mj = {
    "term": {"@id": "resourceUseEnergyDepletionInputsProduction", "termType": "resourceUse", "units": "MJ"},
    "value": 5,
    "inputs": [input_nuclear_fuel_mj]}


@mark.parametrize(
    "resources, expected, num_inputs",
    [
        ([], False, 0),
        ([wrong_indicator], False, 0),
        ([indicator_no_inputs], False, 0),
        ([indicator_2_inputs], False, 2),
        ([indicator_no_unit], False, 1),
        ([indicator_wrong_unit], False, 1),
        ([indicator_bad_input_id], False, 0),
        ([good_indicator_inputs_production_mj], True, 1),
        ([good_indicator_during_cycle_mj], True, 1),
        ([good_nuclear_indicator_mj], True, 1),
    ],
    ids=["No indicators",
         "wrong indicator",
         "indicator no inputs",
         "indicator 2 inputs",
         "missing unit",
         "wrong unit",
         "input id not in requirements",
         "good input production mj",
         "good during cycle mj",
         "good nuclear fuel use indicator in mj",
         ]
)
@patch(f"{class_path}.get_all_non_renewable_terms", side_effect=fake_get_terms)
def test_should_run(mock_get_all_non_renewable_terms, resources, expected, num_inputs):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    impactassessment['emissionsResourceUse'] = resources

    should_run, resources = _should_run(impactassessment)
    assert should_run is expected
    assert len(resources) == num_inputs


@patch(f"{class_path}.get_all_non_renewable_terms", side_effect=fake_get_terms)
@patch(f"{class_path}._indicator", side_effect=fake_rounded_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impactassessment)
    assert value == expected


def test_get_all_non_renewable_terms(*args):
    """
    make sure get_all_non_renewable_terms() only returns terms we want
    """
    electricity_terms = get_all_non_renewable_terms("electricity.csv", "consideredFossilFuelUnderCml2001Baseline")

    assert "electricityGridHardCoal" in electricity_terms
    assert "electricityGridWind" not in electricity_terms

    fuel_terms = get_all_non_renewable_terms("fuel.csv", "consideredFossilFuelUnderCml2001Baseline")

    assert "coalTar" in fuel_terms
    assert "sodPeat" in fuel_terms
    assert "bioJetKerosene" not in fuel_terms
