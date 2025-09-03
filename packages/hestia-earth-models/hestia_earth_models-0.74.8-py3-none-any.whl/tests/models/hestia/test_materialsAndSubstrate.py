from unittest.mock import patch
import json
import pytest
from hestia_earth.utils.tools import to_precision

from tests.utils import fixtures_path, fake_new_input
from hestia_earth.models.hestia.materialAndSubstrate import MODEL, MODEL_KEY, run, calculate_value

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@pytest.mark.parametrize(
    "input_node,cycle_duration,expected_result,test_name",
    [
        (
            {"lifespan": 3, "value": [150]},
            200,
            27.4,
            "lifespan, value and duration"
        ),
        (
            {"lifespan": 5},
            200,
            None,
            "missing value"
        ),
    ]
)
def test_calculate_value(input_node, cycle_duration, expected_result, test_name):
    result = calculate_value(
        input_node=input_node,
        field_name="value",
        cycle_duration=cycle_duration
    )
    rounded_result = to_precision(result, 3) if result is not None else None
    assert rounded_result == expected_result, test_name


@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected
