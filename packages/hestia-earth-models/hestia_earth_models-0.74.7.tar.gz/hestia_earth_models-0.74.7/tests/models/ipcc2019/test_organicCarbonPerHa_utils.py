from pytest import mark

from hestia_earth.models.ipcc2019.organicCarbonPerHa_utils import (
    format_bool, format_bool_list, format_enum, format_number, format_number_list, IpccSoilCategory
)


@mark.parametrize(
    "value, expected",
    [
        (True, "True"),
        (False, "False"),
        ([], "False"),
        ("str", "True"),
        (None, "False")
    ],
    ids=["True", "False", "list", "str", "None"]
)
def test_format_bool(value, expected):
    assert format_bool(value) == expected


@mark.parametrize(
    "value, expected",
    [
        ([True, True, False], "True True False"),
        ([], "None"),
        (["Yes", "No", ""], "True True False"),
        (None, "None")
    ],
    ids=["list", "empty list", "list[str]", "None"]
)
def test_format_bool_list(value, expected):
    assert format_bool_list(value) == expected


@mark.parametrize(
    "value, expected",
    [
        (IpccSoilCategory.WETLAND_SOILS, IpccSoilCategory.WETLAND_SOILS.value),
        ("str", "None"),
        (None, "None")
    ],
    ids=["Enum", "str", "None"]
)
def test_format_enum(value, expected):
    assert format_enum(value) == expected


@mark.parametrize(
    "value, expected",
    [
        (3.141592653, "3.1"),
        (0, "0.0"),
        ("20", "None"),
        (None, "None")
    ],
    ids=["float", "zero", "str", "None"]
)
def test_format_number(value, expected):
    assert format_number(value) == expected


@mark.parametrize(
    "value, expected",
    [
        ([3.14, 31.4, 314], "3.1 31.4 314.0"),
        ([], "None"),
        (["Yes", "No", ""], "None None None"),
        (None, "None")
    ],
    ids=["list", "empty list", "list[str]", "None"]
)
def test_format_number_list(value, expected):
    assert format_number_list(value) == expected
