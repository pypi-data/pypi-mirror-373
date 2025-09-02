import json
from pytest import mark
from unittest.mock import patch

from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.hestia.organicCarbonPerHa import (
    MODEL, TERM_ID, run, _cdf, _c_to_depth, _get_most_relevant_soc_node, _get_last_date
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

SUBFOLDERS = [
    "calculate-single",
    "calculate-multiple",
    "calculate-multiple-with-existing-soc-measurements",  # Closes #823
    "calculate-multiple-with-multiple-methods",  # Closes #823
    "rescale-single",
    "rescale-multiple",
    "calculate-and-rescale"
]


@mark.parametrize("depth, expected", [(0, 0), (1, 10.41666666666667)], ids=["0m", "1m"])
def test_c_to_depth(depth, expected):
    assert _c_to_depth(depth) == expected


@mark.parametrize(
    "depth_upper, depth_lower, expected",
    [(0, 0, 0), (0, 0.3, 0.5054975999999999), (0, 1, 1)],
    ids=["0-0m", "0-0.3m", "0-1m"]
)
def test_cdf(depth_upper, depth_lower, expected):
    assert _cdf(depth_upper, depth_lower) == expected


@mark.parametrize(
    "dates, expected",
    [
        (["2020", "2021", "2020"], "2021"),
        (["2020-01", "2020-02"], "2020-02"),
        (["2020-01-01", "2020-02-28"], "2020-02-28"),
        ([], None)
    ],
    ids=["YYYY", "YYYY-MM", "YYYY-MM-DD", "empty-list"]
)
def test_get_node_date(dates, expected):
    assert _get_last_date(dates) == expected


@mark.parametrize(
    "nodes, expected_id",
    [
        (
            [
                {"@id": "1", "depthUpper": 0, "depthLower": 10},
                {"@id": "2", "depthUpper": 0, "depthLower": 40},
                {"@id": "3", "depthUpper": 0, "depthLower": 100}
            ],
            "2"
        ),
        (
            [
                {"@id": "1", "depthUpper": 0, "depthLower": 5},
                {"@id": "2", "depthUpper": 0, "depthLower": 10},
                {"@id": "3", "depthUpper": 0, "depthLower": 20}
            ],
            "3"
        ),
        (
            [
                {"@id": "1", "depthUpper": 0, "depthLower": 20},
                {"@id": "2", "depthUpper": 0, "depthLower": 40},
                {"@id": "3", "depthUpper": 0, "depthLower": 100}
            ],
            "2"
        )
    ],
    ids=["simple", "no-priority", "tie"]
)
def test_get_most_relevant_soc_node(nodes, expected_id):
    assert _get_most_relevant_soc_node(nodes).get("@id") == expected_id


@mark.parametrize("subfolder", SUBFOLDERS)
@patch(f"{class_path}.get_source", return_value={})
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(_new_measurement_mock, get_source_mock, subfolder):
    with open(f"{fixtures_folder}/{subfolder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/{subfolder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(site)
    assert value == expected


@patch(f"{class_path}.get_source", return_value={})
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run_empty(_new_measurement_mock, get_source_mock):
    assert run({}) == []
