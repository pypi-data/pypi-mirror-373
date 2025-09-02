from unittest.mock import patch
import json
from tests.utils import RESIDUE_TERMS, fixtures_path, fake_new_practice

from hestia_earth.models.koble2014 import MODEL
from hestia_earth.models.koble2014.residueLeftOnField import TERM_ID, run

fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"hestia_earth.models.{MODEL}.utils.get_crop_residue_management_terms", return_value=RESIDUE_TERMS)
@patch(f"hestia_earth.models.{MODEL}.utils._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
