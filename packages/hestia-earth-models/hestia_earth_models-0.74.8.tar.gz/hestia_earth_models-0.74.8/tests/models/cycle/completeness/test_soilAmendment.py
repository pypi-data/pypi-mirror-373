from unittest.mock import patch

from hestia_earth.models.cycle.completeness.soilAmendment import run, MODEL_KEY

class_path = f"hestia_earth.models.cycle.completeness.{MODEL_KEY}"


@patch(f"{class_path}.most_relevant_blank_node_by_id")
def test_run(mock_measurement):
    measurement = {}
    mock_measurement.return_value = measurement

    # with soil ph below 6.5 => not complete
    measurement['value'] = [6]
    assert not run({})

    # with soil ph above 6.5 => not complete
    measurement['value'] = [7]
    assert not run({})

    # with added soil ph => complete
    measurement['added'] = ['value']
    assert run({}) is True
