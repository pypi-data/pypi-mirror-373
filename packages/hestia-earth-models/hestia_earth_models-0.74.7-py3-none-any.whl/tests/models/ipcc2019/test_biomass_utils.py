from pytest import mark

from hestia_earth.models.ipcc2019.biomass_utils import (
    _assign_biomass_category, _get_sample_func, _rescale_category_cover, BiomassCategory, detect_land_cover_change,
    sample_constant, sample_plus_minus_error
)

_ITERATIONS = 1000


# input, expected
PARAMS_RESCALE_CATEGORY_COVER = [
    (
        {BiomassCategory.ANNUAL_CROPS: 90},
        {BiomassCategory.ANNUAL_CROPS: 90, BiomassCategory.OTHER: 10}
    ),
    (
        {BiomassCategory.OTHER: 90},
        {BiomassCategory.OTHER: 100}
    ),
    (
        {BiomassCategory.ANNUAL_CROPS: 60, BiomassCategory.VINE: 60},
        {BiomassCategory.ANNUAL_CROPS: 50, BiomassCategory.VINE: 50}
    ),
    (
        {BiomassCategory.NATURAL_FOREST: 100},
        {BiomassCategory.NATURAL_FOREST: 100}
    )
]
IDS_RESCALE_CATEGORY_COVER = ["fill", "fill w/ other", "squash", "do nothing"]


@mark.parametrize("input, expected", PARAMS_RESCALE_CATEGORY_COVER, ids=IDS_RESCALE_CATEGORY_COVER)
def test_rescale_category_cover(input: dict, expected: dict):
    assert _rescale_category_cover(input) == expected


# a, b, expected
PARAMS_IS_LCC_EVENT = [
    (
        {
            "appleTree": 33.333,
            "pearTree": 33.333,
            BiomassCategory.ANNUAL_CROPS: 33.334,
        },
        {
            "appleTree": 33.33333,
            "pearTree": 33.33333,
            BiomassCategory.ANNUAL_CROPS: 33.33334,
        },
        True
    ),
    (
        {
            "appleTree": 33.3333,
            "pearTree": 33.3333,
            BiomassCategory.ANNUAL_CROPS: 33.3334,
        },
        {
            "appleTree": 33.33333,
            "pearTree": 33.33333,
            BiomassCategory.ANNUAL_CROPS: 33.33334,
        },
        False
    )
]
IDS_IS_LCC_EVENT = ["True", "False"]


@mark.parametrize("a, b, expected", PARAMS_IS_LCC_EVENT, ids=IDS_IS_LCC_EVENT)
def test_detect_land_cover_change(a: dict, b: dict, expected: bool):
    assert detect_land_cover_change(a, b) is expected


# kwargs, sample_func, expected_shape
PARAMS_GET_SAMPLE_FUNC = [
    ({"value": 1}, sample_constant),
    ({"value": 1, "error": 10}, sample_plus_minus_error),
]
IDS_GET_SAMPLE_FUNC = ["constant", "+/- error"]


@mark.parametrize("kwargs, sample_func", PARAMS_GET_SAMPLE_FUNC, ids=IDS_GET_SAMPLE_FUNC)
def test_get_sample_func(kwargs, sample_func):
    result = _get_sample_func(kwargs)
    assert result == sample_func


# input, expected
PARAMS_ASSIGN_BIOMASS_CATEGORY = [
    ("Annual crops", BiomassCategory.ANNUAL_CROPS),
    ("Coconut", BiomassCategory.COCONUT),
    ("Forest", BiomassCategory.FOREST),
    ("Grassland", BiomassCategory.GRASSLAND),
    ("Jatropha", BiomassCategory.JATROPHA),
    ("Jojoba", BiomassCategory.JOJOBA),
    ("Natural forest", BiomassCategory.NATURAL_FOREST),
    ("Oil palm", BiomassCategory.OIL_PALM),
    ("Olive", BiomassCategory.OLIVE),
    ("Orchard", BiomassCategory.ORCHARD),
    ("Other", BiomassCategory.OTHER),
    ("Plantation forest", BiomassCategory.PLANTATION_FOREST),
    ("Rubber", BiomassCategory.RUBBER),
    ("Short rotation coppice", BiomassCategory.SHORT_ROTATION_COPPICE),
    ("Tea", BiomassCategory.TEA),
    ("Vine", BiomassCategory.VINE),
    ("Woody perennial", BiomassCategory.WOODY_PERENNIAL),
    ("Miscellaneous value", None)
]
IDS_ASSIGN_BIOMASS_CATEGORY = [p[0] for p in PARAMS_ASSIGN_BIOMASS_CATEGORY]


@mark.parametrize("input, expected", PARAMS_ASSIGN_BIOMASS_CATEGORY, ids=IDS_ASSIGN_BIOMASS_CATEGORY)
def test_assign_biomass_category(input: str, expected: BiomassCategory):
    assert _assign_biomass_category(input) == expected
