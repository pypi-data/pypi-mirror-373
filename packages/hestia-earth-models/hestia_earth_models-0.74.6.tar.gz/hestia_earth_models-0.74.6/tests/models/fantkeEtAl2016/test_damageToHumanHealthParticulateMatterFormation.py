import json
from unittest.mock import patch

from hestia_earth.models.fantkeEtAl2016.damageToHumanHealthParticulateMatterFormation import MODEL, TERM_ID, run
from tests.utils import fixtures_path, fake_new_indicator

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(mocked_indicator):
    with open(f"{fixtures_folder}/impactassessment.jsonld", encoding='utf-8') as f:
        impactassessment = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impactassessment)
    assert value == expected
