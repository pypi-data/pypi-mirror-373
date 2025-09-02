from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2006.n2OToAirCropResidueDecompositionIndirect import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    # no emissions => no run
    cycle = {'completeness': {'cropResidue': True}, 'emissions': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with no3 emission => run
    cycle['emissions'] = [
        {
            'term': {'@id': 'no3ToGroundwaterCropResidueDecomposition'},
            'value': [100]
        },
        {
            'term': {'@id': 'nh3ToAirCropResidueDecomposition'},
            'value': [100]
        },
        {
            'term': {'@id': 'noxToAirCropResidueDecomposition'},
            'value': [100]
        }
    ]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
