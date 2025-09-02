import json
from unittest.mock import patch

from hestia_earth.models.poschEtAl2008.terrestrialEutrophicationPotentialAccumulatedExceedance import MODEL, TERM_ID, \
    run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def fake_rounded_indicator(value: float):
    indicator = fake_new_indicator(TERM_ID, MODEL)
    indicator['value'] = round(value, 7)
    return indicator


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    with open(f"{fixtures_folder}/Belarus/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impactassessment)
    assert value == expected


@patch(f"{class_path}._indicator", side_effect=fake_rounded_indicator)
def test_lookup_to_bad_country(*args):
    """
    Should default to region-world value
    """
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    impactassessment['country']['@id'] = "example-land-not-real"

    with open(f"{fixtures_folder}/region-world/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impactassessment)
    assert value == expected
