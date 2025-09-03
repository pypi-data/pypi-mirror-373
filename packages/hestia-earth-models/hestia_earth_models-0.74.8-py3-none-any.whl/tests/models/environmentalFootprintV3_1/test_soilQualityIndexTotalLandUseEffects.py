import json
from unittest.mock import patch

from pytest import mark

from hestia_earth.models.environmentalFootprintV3_1 import MODEL_FOLDER
from hestia_earth.models.environmentalFootprintV3_1.soilQualityIndexTotalLandUseEffects import TERM_ID, run, _should_run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL_FOLDER}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL_FOLDER}/{TERM_ID}"

transform_indicator = {
    "term": {
        "@id": "soilQualityIndexLandTransformation",
        "termType": "characterisedIndicator",
    },
    "value": 10,
}
occupation_indicator = {
    "term": {
        "@id": "soilQualityIndexLandOccupation",
        "termType": "characterisedIndicator",
    },
    "value": 10,
}
missing_value_indicator = {
    "term": {
        "@id": "soilQualityIndexLandOccupation",
        "termType": "characterisedIndicator",
    }
}
bad_value_indicator = {
    "term": {
        "@id": "soilQualityIndexLandOccupation",
        "termType": "characterisedIndicator",
    },
    "value": "42",
}


@mark.parametrize(
    "impacts, expected, num_expected",
    [
        ([], False, 0),
        ([transform_indicator], False, 1),
        ([transform_indicator, transform_indicator], False, 2),
        ([transform_indicator, missing_value_indicator], False, 2),
        ([transform_indicator, bad_value_indicator], False, 2),
        ([transform_indicator, occupation_indicator], True, 2),
        ([occupation_indicator], False, 1),
        ([occupation_indicator, occupation_indicator, occupation_indicator,
          transform_indicator, transform_indicator], True, 5),
    ],
    ids=["Empty", "missing obligatory occupation", "duplicate entry", "no value in entry", "bad value in entry",
         "correct assessment", "just occupation", "multiple occupations and transformations"]
)
def test_should_run(impacts, expected, num_expected):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    impactassessment['impacts'] = impacts

    should_run, indicators = _should_run(impactassessment)
    assert should_run is expected
    assert len(indicators) is num_expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impactassessment)
    assert value == expected
