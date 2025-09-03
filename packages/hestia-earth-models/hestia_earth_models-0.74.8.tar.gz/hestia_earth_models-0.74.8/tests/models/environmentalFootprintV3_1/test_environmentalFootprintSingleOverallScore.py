import json
from pytest import mark
from unittest.mock import patch, Mock

from hestia_earth.models.environmentalFootprintV3_1 import MODEL_FOLDER
from hestia_earth.models.environmentalFootprintV3_1.environmentalFootprintSingleOverallScore import MODEL, TERM_ID, \
    run, _should_run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL_FOLDER}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL_FOLDER}/{TERM_ID}"


def fake_rounded_indicator(value: float):
    indicator = fake_new_indicator(TERM_ID, MODEL)
    indicator['value'] = round(value, 20)
    return indicator


methodModelEFV31 = {"@type": "Term", "@id": "environmentalFootprintV3-1"}
methodModelFantkeEtAl2016 = {"@type": "Term", "@id": "fantkeEtAl2016"}
methodModelfrischknechtEtAl2000 = {"@type": "Term", "@id": "frischknechtEtAl2000"}

ozone_indicator = {"@type": "Indicator",
                   "term": {"@id": "ozoneDepletionPotential", "termType": "characterisedIndicator"},
                   "value": 0,
                   "methodModel": {"@type": "Term", "@id": "edip2003"}}

other_valid_ozone_indicator = {"@type": "Indicator",
                               "term": {"@id": "ozoneDepletionPotential", "termType": "characterisedIndicator"},
                               "value": 0,
                               "methodModel": {"@type": "Term", "@id": "recipe2016Hierarchist"}}
acid_indicator = {
    "@type": "Indicator",
    "term": {"@id": "terrestrialAcidificationPotentialAccumulatedExceedance", "termType": "characterisedIndicator"},
    "value": 0.000420443840380047,
    "methodModel": {"@type": "Term", "@id": "poschEtAl2008"}
}

bad_indicator_id = {"@type": "Indicator",
                    "term": {"@id": "no_a_real_id", "termType": "characterisedIndicator"},
                    "value": 0.000420443840380047,
                    "methodModel": methodModelEFV31
                    }

not_pef_indicator = {"@type": "Indicator",
                     "term": {"@id": "gwpStar", "termType": "characterisedIndicator"},
                     "value": 0.000420443840380047,
                     "methodModel": methodModelEFV31
                     }

bad_indicator_no_val = {"@type": "Indicator",
                        "term": {"@id": "damageToHumanHealthParticulateMatterFormation",
                                 "termType": "characterisedIndicator"},
                        "methodModel": methodModelFantkeEtAl2016
                        }

bad_indicator_bad_val = {"@type": "Indicator",
                         "term": {"@id": "damageToHumanHealthParticulateMatterFormation",
                                  "termType": "characterisedIndicator"},
                         "value": None,
                         "methodModel": methodModelFantkeEtAl2016
                         }

bad_indicator_no_method_model = {
    "@type": "Indicator",
    "term": {"@id": "terrestrialAcidificationPotentialAccumulatedExceedance", "termType": "characterisedIndicator"},
    "value": 0.000420443840380047
}

ionising_radiation_indicator_radon = {
    "@type": "Indicator",
    "term": {"@id": "ionisingRadiationKbqU235Eq", "termType": "characterisedIndicator"},
    "value": 0.11156637927360424,
    "key": {"@id": "radon222"},
    "methodModel": methodModelfrischknechtEtAl2000
}

ionising_radiation_indicator_plutonium238 = {
    "@type": "Indicator",
    "term": {"@id": "ionisingRadiationKbqU235Eq", "termType": "characterisedIndicator"},
    "value": 8.567909489437642e-13,
    "key": {"@id": "plutonium238"},
    "methodModel": methodModelfrischknechtEtAl2000
}


@mark.parametrize(
    "impacts, expected, num_inputs",
    [
        ([], False, 0),
        ([bad_indicator_id], False, 0),
        ([not_pef_indicator], False, 0),
        ([bad_indicator_no_val], False, 0),
        ([bad_indicator_bad_val], False, 0),
        ([bad_indicator_no_method_model], False, 0),
        ([other_valid_ozone_indicator], False, 0),
        ([ozone_indicator], True, 1),
        ([ozone_indicator, ozone_indicator], False, 2),
        ([ozone_indicator, acid_indicator], True, 2),
        ([ozone_indicator, other_valid_ozone_indicator], True, 1),
        ([bad_indicator_no_val, acid_indicator], False, 1),
        ([ionising_radiation_indicator_radon, ionising_radiation_indicator_plutonium238], True, 2),
        ([ionising_radiation_indicator_radon, ionising_radiation_indicator_radon], False, 2),
    ],
    ids=[
        "No indicators => no run",
        "bad_indicator_id => no run",
        "not_pef_indicator => no run",
        "bad_indicator_no_val => no run",
        "bad_indicator_bad_val => no run",
        "bad_indicator_no_method_model =>  no run",
        "ozone_indicator not pef=> no run",
        "ozone_indicator pef => run",
        "2 ozone_indicator => no run",
        "2 good indicators => run",
        "2 ozone_indicator different methodModel => run with 1",
        "one bad one good indicator => no run",
        "multiple radiation indicators => run with 2",
        "duplicate radiation indicators => no run",
    ]
)
def test_should_run(impacts, expected, num_inputs):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    impactassessment['impacts'] = impacts

    should_run, resources = _should_run(impactassessment)
    assert should_run is expected
    assert len(resources) == num_inputs


@patch(f"{class_path}._indicator", side_effect=fake_rounded_indicator)
def test_run(_mocked_indicator: Mock, *args):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impactassessment)
    assert value == expected
