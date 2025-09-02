from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019 import MODEL
from hestia_earth.models.ipcc2019.n2OToAirOrganicSoilCultivationIndirect import TERM_ID, run

utils_path = f"hestia_earth.models.{MODEL}.n2OToAir_indirect_emissions_utils"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{utils_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{utils_path}._new_emission", side_effect=fake_new_emission)
def test_run_wet(*args):
    with open(f"{fixtures_folder}/ecoClimateZone-wet/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/ecoClimateZone-wet/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{utils_path}._new_emission", side_effect=fake_new_emission)
def test_run_dry(*args):
    with open(f"{fixtures_folder}/ecoClimateZone-dry/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/ecoClimateZone-dry/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
