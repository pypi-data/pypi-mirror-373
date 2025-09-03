from unittest.mock import patch
import json
from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path, fake_new_input

from hestia_earth.models.transformation.input.excreta import (
    MODEL, MODEL_KEY, run, _should_run, _should_run_transformation
)

class_path = f"hestia_earth.models.{MODEL}.input.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/input/{MODEL_KEY}"


def test_should_run():
    # not a cycle => no run
    data = {'@type': 'Transformation'}
    assert not _should_run(data)

    # as a cycle and no transformations => no run
    data = {'@type': 'Cycle', 'transformations': []}
    assert not _should_run(data)

    # with a transformation => run
    data['transformations'] = [{}]
    assert _should_run(data) is True


def test_should_run_transformation():
    transformation = {'term': {}}

    # not an excreta management => no run
    transformation['term']['termType'] = TermTermType.ANIMALMANAGEMENT.value
    assert not _should_run_transformation(transformation)

    # is an excreta management => no run
    transformation['term']['termType'] = TermTermType.EXCRETAMANAGEMENT.value
    assert _should_run_transformation(transformation) is True


@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
