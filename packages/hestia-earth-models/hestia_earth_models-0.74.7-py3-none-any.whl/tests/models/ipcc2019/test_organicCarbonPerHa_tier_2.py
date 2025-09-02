from numpy import array
from numpy.testing import assert_array_almost_equal
from numpy.typing import NDArray
from pytest import mark

from hestia_earth.utils.stats import discrete_uniform_2d, repeat_single

from hestia_earth.models.ipcc2019.organicCarbonPerHa import MODEL, TERM_ID
from hestia_earth.models.ipcc2019.organicCarbonPerHa_tier_2 import (
    _calc_temperature_factor_annual, _calc_water_factor_annual, _Parameter, _sample_parameter
)

from tests.utils import fixtures_path

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}_tier_2"
utils_path = f"hestia_earth.models.{MODEL}.{TERM_ID}_utils"
term_path = "hestia_earth.models.utils.term"
property_path = "hestia_earth.models.utils.property"

fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

ITERATIONS = 1000
SEED = 0
YEARS = 100
MONTHS = 12


def assert_elements_between(arr: NDArray, min: float, max: float):
    assert ((min <= arr) & (arr <= max)).all()


def assert_rows_unique(arr: NDArray):
    """
    Covert array to a set to remove repeated rows and check that number remaining rows is the same as the number of
    original rows.
    """
    assert len(set(map(tuple, arr))) == len(arr)


PARAMS_SAMPLE_PARAMETER = [p for p in _Parameter]
IDS_SAMPLE_PARAMETER = [p.name for p in _Parameter]


@mark.parametrize("parameter", PARAMS_SAMPLE_PARAMETER, ids=IDS_SAMPLE_PARAMETER)
def test_sample_parameter(parameter):
    """
    Check that every parameter can be sampled without raising an error.
    """
    EXPECTED_SHAPE = (1, ITERATIONS)
    result = _sample_parameter(ITERATIONS, parameter)
    assert result.shape == EXPECTED_SHAPE


# temperature_monthly, expected
PARAMS_TEMPERATURE_FACTOR = [
    (array([[-100] for _ in range(12)]), array([[1.4946486e-27]])),
    (array([[0] for _ in range(12)]), array([[0.0803555]])),
    (array([[33.69] for _ in range(12)]), array([[1]])),
    (array([[45] for _ in range(12)]), array([[0]])),
    (array([[50] for _ in range(12)]), array([[0]])),
    (
        array([
            [22.71129032258065], [20.310714285714287], [19.479032258064514],
            [14.993333333333334], [11.206451612903225], [9.055],
            [8.008064516129034], [11.254838709677419], [11.276666666666666],
            [14.148387096774192], [19.980000000000004], [16.372580645161293]
        ]),
        array([[0.4904241436936742]])
    )
]
IDS_TEMPERATURE_FACTOR = ["-100", "0", "33.69", "45", "50", "ipcc"]


@mark.parametrize("temperature_monthly, expected", PARAMS_TEMPERATURE_FACTOR, ids=IDS_TEMPERATURE_FACTOR)
def test_calc_annual_temperature_factors(temperature_monthly, expected):
    result = _calc_temperature_factor_annual(temperature_monthly)
    assert_array_almost_equal(result, expected)


def test_calc_annual_temperature_factors_random():
    SHAPE = (YEARS * MONTHS, ITERATIONS)
    MIN, MAX = 0, 1

    TEMPERATURE_MONTHLY = discrete_uniform_2d(SHAPE, -60, 60, seed=SEED)

    result = _calc_temperature_factor_annual(TEMPERATURE_MONTHLY)

    assert_elements_between(result, MIN, MAX)
    assert_rows_unique(result)
    assert result.shape == (YEARS, ITERATIONS)


# precipitation_monthly, pet_monthly, expected
PARAMS_WATER_FACTOR = [
    (array([[0] for _ in range(12)]), array([[0] for _ in range(12)]), array([[2.24942813]])),  # Closes issue 771
    (array([[1] for _ in range(12)]), array([[10000] for _ in range(12)]), array([[0.3195496]])),
    (array([[10000] for _ in range(12)]), array([[1] for _ in range(12)]), array([[2.24942813]])),
    (
        array([
            [4.8], [23.900000000000002], [24.7],
            [3.5999999999999996], [11.3], [11.200000000000001],
            [27.400000000000006], [53], [30.7],
            [39.3], [9.399999999999999], [41.8]
        ]),
        array([
            [253.80000000000007], [214.4], [176.59999999999994],
            [104.19999999999997], [62.79999999999997], [41.59999999999999],
            [45.60000000000001], [64.80000000000001], [91.60000000000001],
            [140.00000000000006], [189.99999999999994], [233.00000000000006]
        ]),
        array([[0.7793321739983536]])
    )
]
IDS_WATER_FACTOR = ["0/0", "1/10000", "10000/1", "ipcc"]


@mark.parametrize("precipitation_monthly, pet_monthly, expected", PARAMS_WATER_FACTOR, ids=IDS_WATER_FACTOR)
def test_calc_calc_annual_water_factors(precipitation_monthly, pet_monthly, expected):
    result = _calc_water_factor_annual(precipitation_monthly, pet_monthly)
    assert_array_almost_equal(result, expected)


def test_calc_calc_annual_water_factors_random():
    SHAPE = (YEARS * MONTHS, ITERATIONS)
    MIN, MAX = 0.31935, 2.24942813

    PRECIPITATION_MONTHLY = discrete_uniform_2d(SHAPE, 0, 1000, seed=SEED)
    PET_MONTHLY = discrete_uniform_2d(SHAPE, 0, 2500, seed=SEED+1)

    result = _calc_water_factor_annual(PRECIPITATION_MONTHLY, PET_MONTHLY)

    assert_elements_between(result, MIN, MAX)
    assert_rows_unique(result)
    assert result.shape == (YEARS, ITERATIONS)


def test_calc_calc_annual_water_factors_irrigated():
    EXPECTED = 0.775 * 1.5

    SHAPE = (YEARS * MONTHS, ITERATIONS)
    PRECIPITATION_MONTHLY = discrete_uniform_2d(SHAPE, 0, 1000, seed=SEED)
    PET_MONTHLY = discrete_uniform_2d(SHAPE, 0, 2500, seed=SEED+1)
    IRRIGATED_MONTHLY = repeat_single(SHAPE, True)

    result = _calc_water_factor_annual(PRECIPITATION_MONTHLY, PET_MONTHLY, IRRIGATED_MONTHLY)

    (result == EXPECTED).all()  # assert all elements in result are the expected value
    assert result.shape == (YEARS, ITERATIONS)
