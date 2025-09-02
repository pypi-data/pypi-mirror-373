import os
import json
from datetime import datetime
import pytest
from pytest import mark
from unittest.mock import patch
from tests.utils import fixtures_path

from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.tools import parse
from hestia_earth.models.utils.blank_node import (
    condense_nodes,
    _calc_datetime_range_intersection_duration,
    _gapfill_datestr,
    _get_datestr_format,
    _run_required,
    _run_model_required,
    cumulative_nodes_match,
    DatestrFormat,
    DatestrGapfillMode,
    DatetimeRange,
    group_nodes_by_year,
    group_nodes_by_year_and_month,
    GroupNodesByYearMode,
    split_node_by_dates,
    _most_recent_nodes,
    _shallowest_node,
    validate_start_date_end_date, _str_dates_match
)


class_path = "hestia_earth.models.utils.blank_node"
fixtures_folder = os.path.join(fixtures_path, 'utils', 'blank_node')
measurement_fixtures_folder = os.path.join(fixtures_path, 'utils', 'measurement')

condense_fixtures_folder = os.path.join(fixtures_folder, 'condense-nodes')
condense_folders = [
    d for d in os.listdir(condense_fixtures_folder) if os.path.isdir(os.path.join(condense_fixtures_folder, d))
]


@pytest.mark.parametrize('folder', condense_folders)
def test_condense_nodes(folder: str):
    fixture_path = os.path.join(condense_fixtures_folder, folder)

    with open(f"{fixture_path}/original.jsonld", encoding='utf-8') as f:
        original = json.load(f)
    with open(f"{fixture_path}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = condense_nodes(original)
    assert value == expected, folder


def test_run_required():
    assert not _run_required('model', 'ch4ToAirAquacultureSystems', {
        'site': {'siteType': SiteSiteType.CROPLAND.value}
    })
    assert _run_required('model', 'ch4ToAirAquacultureSystems', {
        'site': {'siteType': SiteSiteType.POND.value}
    }) is True


def test_run_model_required():
    assert _run_model_required('pooreNemecek2018', 'netPrimaryProduction', {
        'site': {'siteType': SiteSiteType.POND.value}
    }) is True
    assert not _run_model_required('pooreNemecek2018', 'netPrimaryProduction', {
        'site': {'siteType': SiteSiteType.CROPLAND.value}
    })


# --- test cumulative_nodes_match ---


CROP_RESIDUE_NODES = [
    {
        "@type": "Product",
        "term": {
            "@type": "Term",
            "@id": "aboveGroundCropResidueBurnt"
        },
        "value": [20, 25, 30]
    },
    {
        "@type": "Product",
        "term": {
            "@type": "Term",
            "@id": "aboveGroundCropResidueRemoved"
        },
        "value": [10, 15, 20]
    },
    {
        "@type": "Product",
        "term": {
            "@type": "Term",
            "@id": "aboveGroundCropResidueLeftOnField"
        },
        "value": [50]
    },
]


def test_cumulative_nodes_match_true(*args):
    result = cumulative_nodes_match(
        lambda node: node.get("term", {}).get("@id") in [
            "aboveGroundCropResidueBurnt", "aboveGroundCropResidueRemoved"
        ],
        CROP_RESIDUE_NODES,
        cumulative_threshold=35
    )
    assert result is True


def test_cumulative_nodes_match_false(*args):
    result = cumulative_nodes_match(
        lambda node: node.get("term", {}).get("@id") in ["aboveGroundCropResidueLeftOnField"],
        CROP_RESIDUE_NODES,
        cumulative_threshold=100
    )
    assert result is False


def test_cumulative_nodes_match_additional_args():
    with pytest.raises(TypeError):
        cumulative_nodes_match(
            lambda node: node.get("term", {}).get("@id") in ["aboveGroundCropResidueBurnt"],
            CROP_RESIDUE_NODES,
            {"random": True},
            cumulative_threshold=10
        )


# --- test _get_datestr_format ---

DATESTR_YEAR = "2000"
DATESTR_YEAR_MONTH = "2000-01"
DATESTR_YEAR_MONTH_DAY = "2000-01-01"
DATESTR_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND = "2000-01-01T00:00:00"
DATESTR_MONTH = "--01"
DATESTR_MONTH_DAY = "--01-01"


def test_get_date_year():
    """
    Test datestr format `YYYY`.
    """
    assert _get_datestr_format(DATESTR_YEAR) == DatestrFormat.YEAR


def test_get_date_year_month():
    """
    Test datestr format `YYYY-MM`.
    """
    assert _get_datestr_format(DATESTR_YEAR_MONTH) == DatestrFormat.YEAR_MONTH


def test_get_date_year_month_day():
    """
    Test datestr format `YYYY-MM-DD`.
    """
    assert _get_datestr_format(DATESTR_YEAR_MONTH_DAY) == DatestrFormat.YEAR_MONTH_DAY


def test_get_date_year_month_day_hour_minute_second():
    """
    Test datestr format `YYYY-MM-DDTHH:mm:ss`.
    """
    assert (
        _get_datestr_format(DATESTR_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND) ==
        DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
    )


def test_get_date_month():
    """
    Test datestr format `--MM`.

    Should only be found in blank node `dates` field. (Format not permitted in `startDate` or `endDate` fields.)
    """
    assert _get_datestr_format(DATESTR_MONTH) == DatestrFormat.MONTH


def test_get_date_month_day():
    """
    Test datestr format `--MM-DD`.

    Should only be found in blank node `dates` field. (Format not permitted in `startDate` or `endDate` fields.)
    """
    assert _get_datestr_format(DATESTR_MONTH_DAY) == DatestrFormat.MONTH_DAY


def test_get_datestr_format_no_zero_padding():
    DATE_STR = "2000-1"
    assert _get_datestr_format(DATE_STR) is None


def test_str_dates_match():
    assert _str_dates_match("2010", "2010-12-31") is True
    assert _str_dates_match("2010", "2010-01-01") is False
    assert _str_dates_match("2010", "2010-12-31") is True
    assert _str_dates_match("2010", "2010-01") is False

    assert _str_dates_match("2010", "2010-12-31", mode=DatestrGapfillMode.START) is False
    assert _str_dates_match("2010", "2010-01-01", mode=DatestrGapfillMode.START) is True


# --- test _gapfill_datestr ---


def test_complete_datestr_year():
    assert _gapfill_datestr(DATESTR_YEAR) == "2000-01-01T00:00:00"
    assert _gapfill_datestr(DATESTR_YEAR, DatestrGapfillMode.MIDDLE) == "2000-07-01T23:59:59"
    assert _gapfill_datestr(DATESTR_YEAR, DatestrGapfillMode.END) == "2000-12-31T23:59:59"


def test_complete_datestr_year_month():
    assert _gapfill_datestr(DATESTR_YEAR_MONTH) == "2000-01-01T00:00:00"
    assert _gapfill_datestr(DATESTR_YEAR_MONTH, DatestrGapfillMode.MIDDLE) == "2000-01-16T11:59:59"
    assert _gapfill_datestr(DATESTR_YEAR_MONTH, DatestrGapfillMode.END) == "2000-01-31T23:59:59"


def test_complete_datestr_year_month_day():
    assert _gapfill_datestr(DATESTR_YEAR_MONTH_DAY) == "2000-01-01T00:00:00"
    assert _gapfill_datestr(DATESTR_YEAR_MONTH_DAY, DatestrGapfillMode.MIDDLE) == "2000-01-01T11:59:59"
    assert _gapfill_datestr(DATESTR_YEAR_MONTH_DAY, DatestrGapfillMode.END) == "2000-01-01T23:59:59"


def test_gapfill_datestr_feburary():
    """
    Gapfilling February datestrings should take into account leap years
    """
    # Non-leap year
    assert _gapfill_datestr("1981-02") == "1981-02-01T00:00:00"
    assert _gapfill_datestr("1981-02", DatestrGapfillMode.MIDDLE) == "1981-02-14T23:59:59"
    assert _gapfill_datestr("1981-02", DatestrGapfillMode.END) == "1981-02-28T23:59:59"

    # Leap year
    assert _gapfill_datestr("2024-02", DatestrGapfillMode.MIDDLE) == "2024-02-15T11:59:59"
    assert _gapfill_datestr("2024-02", DatestrGapfillMode.END) == "2024-02-29T23:59:59"


def test_complete_datestr_should_not_run():
    """
    Completion should not run, therefore the function should return the datestr without
    modification.
    """
    assert _gapfill_datestr(DATESTR_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND) == DATESTR_YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
    assert _gapfill_datestr(DATESTR_MONTH) == DATESTR_MONTH
    assert _gapfill_datestr(DATESTR_MONTH_DAY) == DATESTR_MONTH_DAY
    assert _gapfill_datestr("") == ""


# --- test _calc_datetime_range_intersection_duration ---


def test_calc_datetime_range_intersection_duration():
    r1 = DatetimeRange(
        start=datetime(2000, 1, 1),
        end=datetime(2002, 1, 1)
    )
    r2 = DatetimeRange(
        start=datetime(2001, 1, 1),
        end=datetime(2003, 1, 1)
    )

    result = _calc_datetime_range_intersection_duration(r1, r2)
    assert result == 31536000


def test_calc_datetime_range_intersection_duration_no_intersection():
    r1 = DatetimeRange(
        start=datetime(2000, 1, 1),
        end=datetime(2000, 12, 31)
    )
    r2 = DatetimeRange(
        start=datetime(2001, 1, 1),
        end=datetime(2001, 12, 31)
    )

    result = _calc_datetime_range_intersection_duration(r1, r2)
    assert result == 0


# --- test group_nodes_by_year ---


def test_group_nodes_by_year_empty_list():
    CYCLES = []
    EXPECTED = {}
    result = group_nodes_by_year(CYCLES)
    assert result == EXPECTED


GROUP_NODES_BY_YEAR_SCENARIO_A_CYCLES = [
    {"@id": "cycle-1a", "endDate": "2002"},
    {"@id": "cycle-2a", "endDate": "2003"},
    {"@id": "cycle-3a", "endDate": "2006", "startDate": "2004"}
]


@mark.parametrize(
    "system_datetime",
    [
        datetime(2024, 5, 1),  # Closes issue 772
        datetime(2024, 1, 1),  # Jan 1st
        datetime(2024, 2, 29),  # Leap year
        datetime(2024, 12, 31),  # Dec 31st
        # 3 random dates...
        datetime(2030, 5, 4),
        datetime(2035, 7, 22),
        datetime(2047, 8, 14)
    ],
    ids=lambda system_datetime: f"system_datetime = {datetime.strftime(system_datetime, r'%Y-%m-%d')}"
)
@patch("hestia_earth.utils.tools.parse")
def test_group_nodes_by_year_scenario_a(mock_parse, system_datetime):
    """
    Datestr in format `YYYY`. Some nodes missing `startDate` field. One multi-year cycle.

    Incomplete datestrs are gapfilled by default; with `endDate` datestrs snapping to the end
    of the calendar year, and `startDate` datestrs snapping to the beginning of the calendar
    year.

    A bug used to occur in this function when it was run on the first day of a calendar month (e.g., 2024-04-01). To
    verify that the bug is fixed we have simulated running the function on a variety of different dates.
    """

    EXPECTED = {
        2002: [{
            "@id": "cycle-1a",
            "endDate": "2002",
            "fraction_of_group_duration": 1.0,
            "fraction_of_node_duration": 1.0
        }],
        2003: [{
            "@id": "cycle-2a",
            "endDate": "2003",
            "fraction_of_group_duration": 1.0,
            "fraction_of_node_duration": 1.0
        }],
        2004: [{
            "@id": "cycle-3a",
            "endDate": "2006",
            "startDate": "2004",
            "fraction_of_group_duration": 1.0,
            "fraction_of_node_duration": 0.33394160583941607
        }],
        2005: [{
            "@id": "cycle-3a",
            "endDate": "2006",
            "startDate": "2004",
            "fraction_of_group_duration": 1.0,
            "fraction_of_node_duration": 0.333029197080292
        }],
        2006: [{
            "@id": "cycle-3a",
            "endDate": "2006",
            "startDate": "2004",
            "fraction_of_group_duration": 1.0,
            "fraction_of_node_duration": 0.333029197080292
        }]
    }

    # As we can't mock builtin method datetime.now(), we have to pass our test system_datetime into the parse function.
    mock_parse.side_effect = lambda *args, **kwargs: parse(*args, default=system_datetime, **kwargs)

    result = group_nodes_by_year(GROUP_NODES_BY_YEAR_SCENARIO_A_CYCLES)
    assert result == EXPECTED


def test_group_nodes_by_year_scenario_a_with_inner_key():

    INNER_KEY = "inner_key"
    EXPECTED = {
        2002: {
            INNER_KEY: [{
                "@id": "cycle-1a",
                "endDate": "2002",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 1.0
            }]
        },
        2003: {
            INNER_KEY: [{
                "@id": "cycle-2a",
                "endDate": "2003",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 1.0
            }]
        },
        2004: {
            INNER_KEY: [{
                "@id": "cycle-3a",
                "endDate": "2006",
                "startDate": "2004",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 0.33394160583941607
            }]
        },
        2005: {
            INNER_KEY: [{
                "@id": "cycle-3a",
                "endDate": "2006",
                "startDate": "2004",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 0.333029197080292
            }]
        },
        2006: {
            INNER_KEY: [{
                "@id": "cycle-3a",
                "endDate": "2006",
                "startDate": "2004",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 0.333029197080292
            }]
        }
    }

    result = group_nodes_by_year(GROUP_NODES_BY_YEAR_SCENARIO_A_CYCLES, inner_key=INNER_KEY)
    assert result == EXPECTED


def test_group_nodes_by_year_scenario_b():
    """
    Datestr in format `YYYY-MM-DD`. Two concurrent cycles (`cycle-3b` & `cycle-4b`).
    """

    CYCLES = [
        {"@id": "cycle-1b", "endDate": "2000-12-31", "startDate": "2000-01-01"},
        {"@id": "cycle-2b", "endDate": "2001-12-31", "startDate": "2001-01-01"},
        {"@id": "cycle-3b", "endDate": "2002-12-31", "startDate": "2002-01-01"},
        {"@id": "cycle-4b", "endDate": "2002-12-31", "startDate": "2002-01-01"}
    ]

    EXPECTED = {
        2000: [
            {
                "@id": "cycle-1b",
                "endDate": "2000-12-31",
                "startDate": "2000-01-01",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 1.0
            }
        ],
        2001: [
            {
                "@id": "cycle-2b",
                "endDate": "2001-12-31",
                "startDate": "2001-01-01",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 1.0
            }
        ],
        2002: [
            {
                "@id": "cycle-3b",
                "endDate": "2002-12-31",
                "startDate": "2002-01-01",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 1.0
            },
            {
                "@id": "cycle-4b",
                "endDate": "2002-12-31",
                "startDate": "2002-01-01",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 1.0
            }
        ]
    }

    result = group_nodes_by_year(CYCLES)
    assert result == EXPECTED


def test_group_nodes_by_year_scenario_c():
    """
    Multiple overlapping 6 month and 12 month cycles.
    """

    CYCLES = [
        {"@id": "cycle-1c", "endDate": "2000-06", "startDate": "2000-01"},
        {"@id": "cycle-2c", "endDate": "2001-12", "startDate": "2000-07"},
        {"@id": "cycle-3c", "endDate": "2001-06", "startDate": "2001-01"},
        {"@id": "cycle-4c", "endDate": "2002-06", "startDate": "2001-07"},
        {"@id": "cycle-5c", "endDate": "2002-12", "startDate": "2002-01"}
    ]

    EXPECTED = {
        2000: [
            {
                "@id": "cycle-1c",
                "endDate": "2000-06",
                "startDate": "2000-01",
                "fraction_of_group_duration": 0.4972677595628415,
                "fraction_of_node_duration": 1.0
            },
            {
                "@id": "cycle-2c",
                "endDate": "2001-12",
                "startDate": "2000-07",
                "fraction_of_group_duration": 0.5027322404371585,
                "fraction_of_node_duration": 0.33515482695810567
            }
        ],
        2001: [
            {
                "@id": "cycle-2c",
                "endDate": "2001-12",
                "startDate": "2000-07",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 0.6648451730418944
            },
            {
                "@id": "cycle-3c",
                "endDate": "2001-06",
                "startDate": "2001-01",
                "fraction_of_group_duration": 0.4958904109589041,
                "fraction_of_node_duration": 1.0
            },
            {
                "@id": "cycle-4c",
                "endDate": "2002-06",
                "startDate": "2001-07",
                "fraction_of_group_duration": 0.5041095890410959,
                "fraction_of_node_duration": 0.5041095890410959
            }
        ],
        2002: [
            {
                "@id": "cycle-4c",
                "endDate": "2002-06",
                "startDate": "2001-07",
                "fraction_of_group_duration": 0.4958904109589041,
                "fraction_of_node_duration": 0.4958904109589041
            },
            {
                "@id": "cycle-5c",
                "endDate": "2002-12",
                "startDate": "2002-01",
                "fraction_of_group_duration": 1.0,
                "fraction_of_node_duration": 1.0
            }
        ]
    }

    result = group_nodes_by_year(CYCLES)
    assert result == EXPECTED


def test_group_nodes_by_year_scenario_d():
    """
    Cases where nodes only overlap with year groups by a small amount.
    Overlaps of less than 30% of a year should be not be included in a
    year group, unless that majority (<50%) of their duration takes place
    within that year.
    """

    MANAGEMENT = [
        {
            "term.@id": "fullTillage",
            "endDate": "2000-11",
            "value": 100
        },
        {
            "term.@id": "fullTillage",
            "endDate": "2001-07",
            "startDate": "2000-12",
            "value": 50
        },
        {
            "term.@id": "noTillage",
            "endDate": "2001-07",
            "startDate": "2000-12",
            "value": 50
        },
        {
            "term.@id": "noTillage",
            "endDate": "2002-01",
            "startDate": "2001-08",
            "value": 100
        },
        {
            "term.@id": "organicFertiliserUsed",
            "endDate": "2000-11",
            "startDate": "2000-09",
            "value": True
        },
        {
            "term.@id": "organicFertiliserUsed",
            "endDate": "2002-06",
            "startDate": "2001-07",
            "value": True
        }
    ]

    EXPECTED = {
        2000: [
            {
                "term.@id": "fullTillage",
                "endDate": "2000-11",
                "value": 100,
                "fraction_of_group_duration": 0.9153005464480874,
                "fraction_of_node_duration": 0.9153005464480874
            },
            {
                "term.@id": "organicFertiliserUsed",
                "endDate": "2000-11",
                "startDate": "2000-09",
                "value": True,
                "fraction_of_group_duration": 0.24863387978142076,
                "fraction_of_node_duration": 1.0
            }
        ],
        2001: [
            {
                "term.@id": "fullTillage",
                "endDate": "2001-07",
                "startDate": "2000-12",
                "value": 50,
                "fraction_of_group_duration": 0.5808219178082191,
                "fraction_of_node_duration": 0.8724279835390947
            },
            {
                "term.@id": "noTillage",
                "endDate": "2001-07",
                "startDate": "2000-12",
                "value": 50,
                "fraction_of_group_duration": 0.5808219178082191,
                "fraction_of_node_duration": 0.8724279835390947
            },
            {
                "term.@id": "noTillage",
                "endDate": "2002-01",
                "startDate": "2001-08",
                "value": 100,
                "fraction_of_group_duration": 0.4191780821917808,
                "fraction_of_node_duration": 0.8315217391304348
            },
            {
                "term.@id": "organicFertiliserUsed",
                "endDate": "2002-06",
                "startDate": "2001-07",
                "value": True,
                "fraction_of_group_duration": 0.5041095890410959,
                "fraction_of_node_duration": 0.5041095890410959
            }
        ],
        2002: [
            {
                "term.@id": "organicFertiliserUsed",
                "endDate": "2002-06",
                "startDate": "2001-07",
                "value": True,
                "fraction_of_group_duration": 0.4958904109589041,
                "fraction_of_node_duration": 0.4958904109589041
            }
        ]
    }

    result = group_nodes_by_year(MANAGEMENT)
    assert result == EXPECTED


def test_group_nodes_by_year_scenario_e():
    """
    Edge case where nodes with short durations are equally split between two
    year groups. In this case, they should be categorised as the later of the
    two potential groups.
    """

    MANAGEMENT = [
        {
            "term.@id": "fullTillage",
            "endDate": "2001-01",
            "startDate": "2000-12",
            "value": 100
        }
    ]

    EXPECTED = {
        2001: [
            {
                "term.@id": "fullTillage",
                "endDate": "2001-01",
                "startDate": "2000-12",
                "value": 100,
                "fraction_of_group_duration": 0.08493150684931507,
                "fraction_of_node_duration": 0.50
            }
        ]
    }

    result = group_nodes_by_year(MANAGEMENT)
    assert result == EXPECTED


def test_group_nodes_by_year_missing_dates():

    NODES = [
        {"value": [0], "endDate": "2000-12-31", "startDate": "2000-01-01"},
        {"value": [1], "endDate": "2000-12-31", "startDate": "2000-01-01"},
        {"value": [2], "endDate": "2001-12-31", "startDate": "2001-01-01"},
        {"value": [3], "dates": ["2001-12-31"]},
        {"value": [4], "dates": ["2002"]},
        {"value": [5], "dates": ["2003-06"]}
    ]

    EXPECTED = {
        2001: [{
            "value": [3],
            "dates": ["2001-12-31"],
            "fraction_of_group_duration": 0.0027397260273972603,
            "fraction_of_node_duration": 1.0
        }],
        2002: [{
            "value": [4],
            "dates": ["2002"],
            "fraction_of_group_duration": 1.0,
            "fraction_of_node_duration": 1.0
        }],
        2003: [{
            "value": [5],
            "dates": ["2003-06"],
            "fraction_of_group_duration": 0.0821917808219178,
            "fraction_of_node_duration": 1.0
        }]
    }

    result = group_nodes_by_year(NODES, mode=GroupNodesByYearMode.DATES)
    assert result == EXPECTED


def test_group_nodes_by_year_incorrect_dates():

    NODES = [
        {"value": [0], "endDate": "2000-09-14", "startDate": "2000-09-15"},
    ]

    EXPECTED = {}

    result = group_nodes_by_year(NODES, mode=GroupNodesByYearMode.START_AND_END_DATE)
    assert result == EXPECTED


@mark.parametrize(
    "system_datetime",
    [
        datetime(2024, 5, 1),  # Closes issue 772
        datetime(2024, 1, 1),  # Jan 1st
        datetime(2024, 2, 29),  # Leap year
        datetime(2024, 12, 31),  # Dec 31st
        # 3 random dates...
        datetime(2026, 5, 14),
        datetime(2032, 10, 10),
        datetime(2043, 8, 22)
    ],
    ids=lambda system_datetime: f"system_datetime = {datetime.strftime(system_datetime, r'%Y-%m-%d')}"
)
@patch("hestia_earth.utils.tools.parse")
def test_group_nodes_by_year_multiple_values_and_dates(mock_parse, system_datetime):
    """
    A bug used to occur in this function when it was run on the first day of a calendar month (e.g., 2024-04-01). To
    verify that the bug is fixed we have simulated running the function on a variety of different dates.
    """

    NODES = [{
        "value": [1, 2, 3, 4, 5],
        "dates": [
            "2000-01",
            "2000-06",
            "2001-02",
            "2002-03",
            "2003-01"
        ],
        "sd": [
            0.8, 0.9, 1.0, 0.9, 0.8
        ],
        "observations": [
            100, 100, 100, 100, 100
        ]
    }]

    EXPECTED = {
        2000: [
            {
                "dates": ["2000-01"],
                "fraction_of_node_duration": 1.0,
                "fraction_of_group_duration": 0.08469945355191257,
                "value": [1],
                "sd": [0.8],
                "observations": [
                    100
                ]
            },
            {
                "dates": ["2000-06"],
                "fraction_of_node_duration": 1.0,
                "fraction_of_group_duration": 0.08196721311475409,
                "value": [2],
                "sd": [0.9],
                "observations": [
                    100
                ]
            }
        ],
        2001: [{
            "dates": ["2001-02"],
            "fraction_of_node_duration": 1.0,
            "fraction_of_group_duration": 0.07671232876712329,
            "value": [3],
            "sd": [1.0],
            "observations": [
                100
            ]
        }],
        2002: [{
            "dates": ["2002-03"],
            "fraction_of_node_duration": 1.0,
            "fraction_of_group_duration": 0.08493150684931507,
            "value": [4],
            "sd": [0.9],
            "observations": [
                100
            ]
        }],
        2003: [{
            "dates": ["2003-01"],
            "fraction_of_node_duration": 1.0,
            "fraction_of_group_duration": 0.08493150684931507,
            "value": [5],
            "sd": [0.8],
            "observations": [
                100
            ]
        }]
    }

    # As we can't mock builtin method datetime.now(), we have to pass our test system_datetime into the parse function.
    mock_parse.side_effect = lambda *args, **kwargs: parse(*args, default=system_datetime, **kwargs)

    result = group_nodes_by_year(NODES, mode=GroupNodesByYearMode.DATES)
    assert result == EXPECTED


@mark.parametrize(
    "system_datetime",
    [
        datetime(2024, 5, 1),  # Closes issue 772
        datetime(2024, 1, 1),  # Jan 1st
        datetime(2024, 2, 29),  # Leap year
        datetime(2024, 12, 31),  # Dec 31st
        # 3 random dates...
        datetime(2026, 4, 6),
        datetime(2034, 7, 24),
        datetime(2049, 10, 10)
    ],
    ids=lambda system_datetime: f"system_datetime = {datetime.strftime(system_datetime, r'%Y-%m-%d')}"
)
@patch("hestia_earth.utils.tools.parse")
def test_group_nodes_by_year_and_month(mock_parse, system_datetime):
    """
    A bug used to occur in this function when it was run on the first day of a calendar month (e.g., 2024-04-01). To
    verify that the bug is fixed we have simulated running the function on a variety of different dates.
    """

    MANAGEMENT = [
        {
            "term.@id": "fullTillage",
            "endDate": "2001-01",
            "startDate": "2000-12",
            "value": 100
        },
        {
            "term.@id": "reducedTillage",
            "endDate": "2001-10",
            "startDate": "2001-09",
            "value": 100
        }
    ]

    EXPECTED = {
        2000: {
            12: [
                {
                    "term.@id": "fullTillage",
                    "endDate": "2001-01",
                    "startDate": "2000-12",
                    "value": 100,
                }
            ]
        },
        2001: {
            1: [
                {
                    "term.@id": "fullTillage",
                    "endDate": "2001-01",
                    "startDate": "2000-12",
                    "value": 100,
                }
            ],
            9: [
                {
                    "term.@id": "reducedTillage",
                    "endDate": "2001-10",
                    "startDate": "2001-09",
                    "value": 100,
                }
            ],
            10: [
                {
                    "term.@id": "reducedTillage",
                    "endDate": "2001-10",
                    "startDate": "2001-09",
                    "value": 100,
                }
            ],
        }
    }

    # As we can't mock builtin method datetime.now(), we have to pass our test system date into the parse function.
    mock_parse.side_effect = lambda *args, **kwargs: parse(*args, default=system_datetime, **kwargs)

    result = group_nodes_by_year_and_month(MANAGEMENT)
    assert result == EXPECTED


# node, expected
PARAMS_SPLIT_NODE = [
    (
        {},
        [{}]
    ),
    (
        {"value": [1, 2, 3], "dates": ["2000"]},
        [{"value": [1, 2, 3], "dates": ["2000"]}]
    ),
    (
        {"value": [1, 2, 3], "startDate": "2000", "endDate": "2001"},
        [{"value": [1, 2, 3], "startDate": "2000", "endDate": "2001"}]
    ),
    (
        {"value": 1, "startDate": "2000", "endDate": "2001"},
        [{"value": 1, "startDate": "2000", "endDate": "2001"}]
    ),
    (
        {"value": None},
        [{"value": None}]
    ),
    (
        {"value": [1, 2, 3], "dates": ["2000", "2001", "2002"]},
        [
            {"value": [1], "dates": ["2000"]},
            {"value": [2], "dates": ["2001"]},
            {"value": [3], "dates": ["2002"]}
        ]
    ),
    (
        {
            "value": [1, 2],
            "dates": ["2000", "2001"],
            "sd": [0.816496, 0.816496],
            "min": [0, 1],
            "max": [2, 3],
            "observations": [3, 3]
        },
        [
            {
                "value": [1],
                "dates": ["2000"],
                "sd": [0.816496],
                "min": [0],
                "max": [2],
                "observations": [3]
            },
            {
                "value": [2],
                "dates": ["2001"],
                "sd": [0.816496],
                "min": [1],
                "max": [3],
                "observations": [3]
            }
        ]
    ),
    (
        {
            "value": [1, 2],
            "dates": ["2000", "2001"],
            "sd": [0.816496, 0.816496],
            "min": [0, 1],
            "max": [2, 3],
            "observations": [3]
        },
        [
            {
                "value": [1],
                "dates": ["2000"],
                "sd": [0.816496],
                "min": [0],
                "max": [2],
                "observations": [3]
            },
            {
                "value": [2],
                "dates": ["2001"],
                "sd": [0.816496],
                "min": [1],
                "max": [3],
                "observations": [3]
            }
        ]
    )
]
IDS_SPLIT_NODE = [
    "no split - empty node",
    "no split - not enough dates",  # len(value) and len(dates) MUST match
    "no split - startDate & endDate",
    "no split - non-iterable value",  # i.e., on a Management or Animal node.
    "no split - null value",  # i.e., on a Animal node where value is not required.
    "value & dates",
    "descriptive statistics",
    "descriptive statistics w/ bad key"  # if descriptive statistic keys have wrong length, don't split them
]


@mark.parametrize("node, expected", PARAMS_SPLIT_NODE, ids=IDS_SPLIT_NODE)
def test_split_node_by_dates(node, expected):
    assert split_node_by_dates(node) == expected


def test_most_recent_measurements():
    with open(f"{measurement_fixtures_folder}/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    with open(f"{measurement_fixtures_folder}/most-recent/measurements.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    assert _most_recent_nodes(measurements, '2011') == expected


def test_shallowest_measurement():
    with open(f"{measurement_fixtures_folder}/most-recent/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    with open(f"{measurement_fixtures_folder}/shallowest/measurement.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    assert _shallowest_node(measurements) == expected


@mark.parametrize(
    "node, expected",
    [
        (
            {"startDate": "2000", "endDate": "2001"},
            True
        ),
        (
            {"startDate": "2001", "endDate": "2000"},
            False
        ),
        (
            {"startDate": "2000-01-01T00:00:00", "endDate": "2000-01-01T00:00:00"},
            False
        ),
        (
            {"endDate": "2000"},
            True
        ),
        (
            {},
            True
        ),
    ],
    ids=["correct", "reversed", "equal", "no start date", "no start date, no end date"])
def test_validate_start_date_end_date(node: dict, expected: bool):
    # Closes #972
    assert validate_start_date_end_date(node) == expected
