import json
from pytest import mark
from unittest.mock import patch
from hestia_earth.schema import MeasurementMethodClassification

from tests.utils import fixtures_path, TERM
from hestia_earth.models.utils.measurement import (
    _new_measurement, most_relevant_measurement_value, min_measurement_method_classification
)

class_path = 'hestia_earth.models.utils.measurement'
fixtures_folder = f"{fixtures_path}/utils/measurement"


@patch(f"{class_path}.include_method", side_effect=lambda n, **kwargs: n)
@patch(f"{class_path}.download_term", return_value=TERM)
def test_new_measurement(*args):
    # with a Term as string
    measurement = _new_measurement('term')
    assert measurement == {
        '@type': 'Measurement',
        'term': TERM
    }

    # with a Term as dict
    measurement = _new_measurement(TERM)
    assert measurement == {
        '@type': 'Measurement',
        'term': TERM
    }


def test_most_relevant_measurement_value_single():
    measurements = [
        {
            'term': {
                '@type': 'Term',
                '@id': 'soilPh'
            },
            'value': [
                2000
            ]
        }
    ]

    assert most_relevant_measurement_value(measurements, 'soilPh', '2011') == 2000


def test_most_relevant_measurement_value_by_year():
    with open(f"{fixtures_folder}/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    assert most_relevant_measurement_value(measurements, 'soilPh', '2011') == 2010


def test_most_relevant_measurement_value_by_year_month():
    with open(f"{fixtures_folder}/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    assert most_relevant_measurement_value(measurements, 'soilPh', '2001-10') == 2001


def test_most_relevant_measurement_value_by_year_month_day():
    with open(f"{fixtures_folder}/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    assert most_relevant_measurement_value(measurements, 'soilPh', '2030-01-07') == 2030


@mark.parametrize(
    "input, expected",
    [
        (
            (
                MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
                MeasurementMethodClassification.TIER_2_MODEL,
                MeasurementMethodClassification.TIER_1_MODEL
            ),
            MeasurementMethodClassification.TIER_1_MODEL
        ),
        (
            [
                MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
                MeasurementMethodClassification.TIER_2_MODEL,
                MeasurementMethodClassification.TIER_1_MODEL
            ],
            MeasurementMethodClassification.TIER_1_MODEL
        ),
        (
            [], MeasurementMethodClassification.UNSOURCED_ASSUMPTION
        ),
        (
            (
                MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT.value,
                MeasurementMethodClassification.TIER_2_MODEL.value,
                MeasurementMethodClassification.TIER_1_MODEL.value
            ),
            MeasurementMethodClassification.TIER_1_MODEL
        ),
        (
            [
                MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT.value,
                MeasurementMethodClassification.TIER_2_MODEL.value,
                MeasurementMethodClassification.TIER_1_MODEL.value
            ],
            MeasurementMethodClassification.TIER_1_MODEL
        ),

    ],
    ids=["Enum", "list[Enum]", "None", "str", "list[str]"]
)
def test_min_measurement_method_classification(input, expected):
    result = min_measurement_method_classification(input)
    assert result == expected
