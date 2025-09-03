import json
from unittest.mock import patch

import pytest

from hestia_earth.models.cml2001Baseline.resourceUseEnergyDepletionDuringCycle import MODEL, TERM_ID, run, _should_run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

diesel_input = {
    "term": {"termType": "fuel", "units": "kg", "@id": "diesel"},
    "value": 2,
    "properties": [{"term": {"@id": "energyContentLowerHeatingValue", }, "value": 70}]
}
diesel_input_in_mj = {
    "term": {"termType": "fuel", "units": "MJ", "@id": "diesel"},
    "value": 111
}
diesel_input_wrong_unit = {
    "term": {"termType": "fuel", "units": "foobedoos", "@id": "diesel"},
    "value": 2
}
diesel_input_no_unit = {
    "term": {"termType": "fuel", "@id": "diesel"},
    "value": 2
}
diesel_input_with_properties = {
    "term": {"termType": "fuel", "units": "kg", "@id": "diesel"},
    "value": 2,
    "properties": [{"term": {"@id": "energyContentLowerHeatingValue", }, "value": 70}]
}
diesel_input_with_properties2 = {
    "term": {"termType": "fuel", "units": "kg", "@id": "diesel"},
    "value": 2,
    "properties": [{"term": {"@id": "energyContentLowerHeatingValue", }, "value": 4}]
}

electricity_input = {
    "term": {"termType": "electricity", "units": "kWh", "@id": "electricityGridOil"},
    "value": 30
}

input_coal_tar_kg = {
    "term": {"@id": "coalTar", "termType": "fuel", "units": "kg", "name": "Coal tar unknown energy Content"},
    "value": 5
}

input_crude_oil_kg_property = {
    "term": {"@id": "conventionalCrudeOil", "termType": "fuel", "units": "kg"},
    "value": 5,
    "properties": [{
        "@type": "Property",
        "value": 45.8,
        "term": {"@type": "Term", "@id": "energyContentLowerHeatingValue", "units": "MJ / kg"},
    }]
}

input_natural_gas_m3 = {
    "term": {"@id": "naturalGas", "termType": "fuel", "units": "m3"},
    "value": 5,
    "properties": [{
        "@type": "Property",
        "value": 45.8,
        "term": {"@type": "Term", "@id": "energyContentLowerHeatingValue", "units": "MJ / kg"},
    }, {
        "@type": "Property",
        "value": 45.8,
        "term": {"@type": "Term", "@id": "density", "units": "kg / m3"},
    }]
}

input_nuclear_fuel_kwh = {
    "term": {"@id": "electricityGridNuclear", "termType": "electricity", "units": "kWh"},
    "value": 1.3889
}


@pytest.mark.parametrize(
    "inputs, expected, num_inputs",
    [
        ([], False, 0),
        ([diesel_input_wrong_unit], False, 0),
        ([diesel_input_no_unit], False, 0),
        ([diesel_input], True, 1),
        ([diesel_input, diesel_input, diesel_input_in_mj], True, 1),
        ([diesel_input, diesel_input_with_properties], True, 1),
        ([diesel_input_with_properties, diesel_input_with_properties], True, 1),
        ([diesel_input_with_properties2, diesel_input_with_properties], True, 1),
        ([electricity_input], True, 1),
        ([electricity_input, electricity_input, electricity_input], True, 1),
        ([input_crude_oil_kg_property], True, 1),
        ([input_natural_gas_m3], True, 1),
        ([input_nuclear_fuel_kwh], True, 1),
        ([input_coal_tar_kg], False, 0),
    ],
    ids=[
        "No inputs => no run, empty input",
        "bad input unit => no run, empty input",
        "bad input no unit => no run, empty input",
        "good fuel input => run",
        "multiple good merg-able fuel inputs => run",
        "multiple good distinct fuel inputs => run",
        "multiple good fuel inputs with same prop=> run",
        "multiple good fuel inputs with distinct prop=> run",
        "good electric input => run",
        "multiple good merg-able electric inputs => run",
        "good fuel with input property",
        "good fuel in m^3",
        "good nuclear fuel use indicator in kWh",
        "bad indicator input in kg no property to convert to mj"
    ]
)
@patch('hestia_earth.models.utils.property.download_term', return_value={})
def test_should_run(mock_download, inputs, expected, num_inputs):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    cycle['inputs'] = inputs

    should_run, grouped_energy_terms = _should_run(cycle)
    assert should_run is expected
    assert len(grouped_energy_terms.keys()) == num_inputs


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
