import json
from unittest.mock import patch

import pytest

from hestia_earth.models.cml2001Baseline.resourceUseMineralsAndMetalsDuringCycle import MODEL, TERM_ID, run, _should_run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

antimony = {"term": {"termType": "material", "@id": "antimony", "units": "kg"}, "value": [3]}
antimony_bad_unit = {"term": {"termType": "material", "@id": "antimony", "units": "boogiewoogiw"}, "value": [3]}
boron = {"term": {"termType": "soilAmendment", "@id": "boron", "units": "kg"}, "value": [3]}
tellurium = {"term": {"termType": "otherInorganicChemical", "@id": "CAS-13494-80-9", "units": "kg"}, "value": [30]}


@pytest.mark.parametrize(
    "cycle_inputs, expected, num_inputs",
    [
        ([], False, 0),
        ([antimony_bad_unit], False, 0),
        ([antimony], True, 1),
        ([antimony, antimony, antimony], True, 1),
        ([antimony, boron], True, 2),
        ([antimony, boron, tellurium], True, 3),

    ],
    ids=[
        "No inputs => no run, empty input",
        "bad input => no run, empty input",
        "good fuel input => run",
        "multiple good merg-able material inputs => run",
        "multiple good non merg-able material inputs => run",
        "all termTypes inputs => run",
    ]
)
def test_should_run(cycle_inputs, expected, num_inputs):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    cycle['inputs'] = cycle_inputs

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
