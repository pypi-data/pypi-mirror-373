from pytest import mark
from typing import Any
from unittest.mock import MagicMock, patch

from hestia_earth.models.utils.ecoClimateZone import (
    _eco_climate_zone_node_value_to_enum, EcoClimateZone, get_eco_climate_zone_value,
    get_ecoClimateZone_lookup_grouped_value
)

class_path = "hestia_earth.models.utils.ecoClimateZone"

# value, expected
PARAMS_TO_ENUM = [
    (0, None),
    (1, EcoClimateZone.WARM_TEMPERATE_MOIST),
    (2, EcoClimateZone.WARM_TEMPERATE_DRY),
    (3, EcoClimateZone.COOL_TEMPERATE_MOIST),
    (4, EcoClimateZone.COOL_TEMPERATE_DRY),
    (5, EcoClimateZone.POLAR_MOIST),
    (6, EcoClimateZone.POLAR_DRY),
    (7, EcoClimateZone.BOREAL_MOIST),
    (8, EcoClimateZone.BOREAL_DRY),
    (9, EcoClimateZone.TROPICAL_MONTANE),
    (10, EcoClimateZone.TROPICAL_WET),
    (11, EcoClimateZone.TROPICAL_MOIST),
    (12, EcoClimateZone.TROPICAL_DRY),
    (13, None),
    ("string", None),
    (None, None)
]
IDS_TO_ENUM = [str(input_) for input_, _ in PARAMS_TO_ENUM]


@mark.parametrize("value, expected", PARAMS_TO_ENUM, ids=IDS_TO_ENUM)
def test_eco_climate_zone_node_value_to_enum(value, expected):
    assert _eco_climate_zone_node_value_to_enum(value) == expected


# node, as_enum, expected
PARAMS_GET_ECZ_VALUE = [
    (
        {
            "@type": "Site",
            "measurements": [
                {
                    "@type": "Measurement",
                    "term": {
                        "@type": "Term",
                        "@id": "ecoClimateZone"
                    },
                    "value": [2],
                }
            ]
        },
        False,
        2
    ),
    (
        {
            "@type": "Site",
            "measurements": [
                {
                    "@type": "Measurement",
                    "term": {
                        "@type": "Term",
                        "@id": "ecoClimateZone"
                    },
                    "value": [2],
                }
            ]
        },
        True,
        EcoClimateZone.WARM_TEMPERATE_DRY
    ),
    (
        {
            "@type": "Cycle",
            "site": {
                "@type": "Site",
                "measurements": [
                    {
                        "@type": "Measurement",
                        "term": {
                            "@type": "Term",
                            "@id": "ecoClimateZone"
                        },
                        "value": [2],
                    }
                ]
            }
        },
        False,
        2
    ),
    (
        {
            "@type": "Cycle",
            "site": {
                "@type": "Site",
                "measurements": [
                    {
                        "@type": "Measurement",
                        "term": {
                            "@type": "Term",
                            "@id": "ecoClimateZone"
                        },
                        "value": [2],
                    }
                ]
            }
        },
        True,
        EcoClimateZone.WARM_TEMPERATE_DRY
    ),
    ({}, False, None),
    ({}, True, None),
]
IDS_GET_ECZ_VALUE = [
    "site", "site as enum",
    "cycle", "cycle as enum",
    "other", "other as enum"
]


@mark.parametrize("node, as_enum, expected", PARAMS_GET_ECZ_VALUE, ids=IDS_GET_ECZ_VALUE)
def test_get_eco_climate_zone_value(node, as_enum, expected):
    assert get_eco_climate_zone_value(node, as_enum=as_enum) == expected


# lookup_return_value, expected
PARAMS_LOOKUP_GROUPED = [
    ("1", None),
    ("-", None),
    ("", None),
    ("value:1", {"value": 1}),
    ("value:-1", {"value": -1}),
    ("value:1;sd:0.5", {"value": 1, "sd": 0.5})
]
IDS_LOOKUP_GROUPED = [p[0] for p in PARAMS_LOOKUP_GROUPED]


@mark.parametrize("lookup_return_value, expected", PARAMS_LOOKUP_GROUPED, ids=IDS_LOOKUP_GROUPED)
@patch(f"{class_path}.download_lookup", return_value=None)
@patch(f"{class_path}._get_single_table_value")
def test_get_ecoClimateZone_lookup_grouped_value(
    get_single_table_value_mock: MagicMock,
    _download_lookup_mock: MagicMock,
    lookup_return_value: str,
    expected: Any
):
    get_single_table_value_mock.return_value = lookup_return_value
    assert get_ecoClimateZone_lookup_grouped_value(1, "TEST") == expected
