from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_indicator, fake_load_impacts

from hestia_earth.models.linkedImpactAssessment.freshwaterWithdrawalsInputsProduction import TERM_ID, run

from hestia_earth.models.linkedImpactAssessment import MODEL
class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
utils_class_path = f"hestia_earth.models.{MODEL}.utils"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{utils_class_path}.load_impacts", side_effect=fake_load_impacts)
@patch(f"{utils_class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
