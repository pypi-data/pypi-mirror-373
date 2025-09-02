from unittest.mock import patch
import json
from tests.utils import fake_new_practice, fixtures_path

from hestia_earth.models.hestia.residueBurnt import MODEL, TERM_ID, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    # no products => no run
    cycle = {'completeness': {'cropResidue': False}, 'products': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with `aboveGroundCropResidueTotal` => no run
    cycle['products'].append({'term': {'@id': 'aboveGroundCropResidueTotal'}, 'value': [10]})
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with `aboveGroundCropResidueBurnt` => run
    cycle['products'].append({'term': {'@id': 'aboveGroundCropResidueBurnt'}, 'value': [10]})
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(data)
    assert result == expected
