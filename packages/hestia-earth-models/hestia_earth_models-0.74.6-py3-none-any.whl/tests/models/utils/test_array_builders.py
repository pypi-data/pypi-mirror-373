from numpy import array, corrcoef
from numpy.testing import assert_array_equal, assert_allclose
from numpy.typing import NDArray
from pytest import mark

from hestia_earth.utils.stats import (
    avg_run_in_columnwise, avg_run_in_rowwise, correlated_normal_2d, discrete_uniform_1d, discrete_uniform_2d,
    gen_seed, grouped_avg, normal_1d, normal_2d, plus_minus_uncertainty_to_normal_1d,
    plus_minus_uncertainty_to_normal_2d, repeat_1d_array_as_columns, repeat_array_as_columns, repeat_array_as_rows,
    repeat_single, triangular_1d, triangular_2d, truncated_normal_1d, truncated_normal_2d
)

SEED = 0
N_ITERATIONS = 10000
SHAPE = (1000, 1000)


def assert_rows_identical(arr: NDArray):
    """
    Covert array to a set to remove repeated rows and check that number remaining rows is 1.
    """
    assert len(set(map(tuple, arr))) == 1


def assert_rows_unique(arr: NDArray):
    """
    Covert array to a set to remove repeated rows and check that number remaining rows is the same as the number of
    original rows.
    """
    assert len(set(map(tuple, arr))) == len(arr)


def assert_elements_between(arr: NDArray, min: float, max: float):
    assert ((min <= arr) & (arr <= max)).all()


PARAMS_REPEAT_SINGLE = [
    (3.14159, None, 3.14159),
    (3.14159, bool, True),
    (True, None, True),
    (True, float, 1)
]

IDS_REPEAT_SINGLE = [
    f"{type(value).__name__}{f' -> {dtype.__name__}' if dtype else ''}" for value, dtype, _ in PARAMS_REPEAT_SINGLE
]


@mark.parametrize(
    "value, dtype, expected_element",
    [(3.14159, None, 3.14159), (3.14159, bool, True), (True, None, True), (True, float, 1)],
    ids=IDS_REPEAT_SINGLE
)
def test_repeat_single(value, dtype, expected_element):
    SHAPE = (3, 3)
    EXPECTED = array([
        [expected_element, expected_element, expected_element],
        [expected_element, expected_element, expected_element],
        [expected_element, expected_element, expected_element]
    ])
    result = repeat_single(SHAPE, value, dtype=dtype)
    assert_array_equal(result, EXPECTED)


def test_repeat_array_as_columns():
    INPUT = array([
        [1, 2, 3],
        [4, 5, 6]
    ])
    EXPECTED = array([
        [1, 2, 3, 1, 2, 3],
        [4, 5, 6, 4, 5, 6]
    ])
    result = repeat_array_as_columns(2, INPUT)
    assert_array_equal(result, EXPECTED)


def test_repeat_array_as_rows():
    INPUT = array([
        [1, 2, 3],
        [4, 5, 6]
    ])
    EXPECTED = array([
        [1, 2, 3],
        [4, 5, 6],
        [1, 2, 3],
        [4, 5, 6]
    ])
    result = repeat_array_as_rows(2, INPUT)
    assert_array_equal(result, EXPECTED)


def test_repeat_1d_array_as_columns():
    INPUT = array([1, 2, 3])
    EXPECTED = array([
        [1, 1, 1],
        [2, 2, 2],
        [3, 3, 3]
    ])
    result = repeat_1d_array_as_columns(3, INPUT)
    assert_array_equal(result, EXPECTED)


def test_discrete_uniform_1d():
    MIN, MAX = -100, 100
    result = discrete_uniform_1d(SHAPE, MIN, MAX, seed=SEED)
    assert_rows_identical(result)
    assert_elements_between(result, MIN, MAX)
    assert result.shape == SHAPE


def test_discrete_uniform_2d():
    MIN, MAX = -100, 100
    result = discrete_uniform_2d(SHAPE, MIN, MAX, seed=SEED)
    assert_rows_unique(result)
    assert_elements_between(result, MIN, MAX)
    assert result.shape == SHAPE


def test_discrete_triangular_1d():
    LOW, HIGH = -100, 100
    MODE = -50
    result = triangular_1d(SHAPE, LOW, HIGH, MODE, seed=SEED)
    assert_rows_identical(result)
    assert_elements_between(result, LOW, HIGH)
    assert result.shape == SHAPE


def test_discrete_triangular_2d():
    LOW, HIGH = -100, 100
    MODE = 50
    result = triangular_2d(SHAPE, LOW, HIGH, MODE, seed=SEED)
    assert_rows_unique(result)
    assert_elements_between(result, LOW, HIGH)
    assert result.shape == SHAPE


def test_normal_1d():
    MEAN = 0
    SD = 50
    result = normal_1d(SHAPE, MEAN, SD, seed=SEED)
    assert_rows_identical(result)
    assert result.shape == SHAPE


def test_normal_2d():
    MEAN = 0
    SD = 50
    result = normal_2d(SHAPE, MEAN, SD, seed=SEED)
    assert_rows_unique(result)
    assert result.shape == SHAPE


def test_truncated_normal_1d():
    MEAN = 0
    SD = 50
    LOW, HIGH = -50, 50
    result = truncated_normal_1d(SHAPE, MEAN, SD, LOW, HIGH, seed=SEED)
    assert_rows_identical(result)
    assert_elements_between(result, LOW, HIGH)
    assert result.shape == SHAPE


def test_truncated_normal_2d():
    MEAN = 0
    SD = 50
    LOW, HIGH = -50, 50
    result = truncated_normal_2d(SHAPE, MEAN, SD, LOW, HIGH, seed=SEED)
    assert_rows_unique(result)
    assert_elements_between(result, LOW, HIGH)
    assert result.shape == SHAPE


def test_plus_minus_uncertainty_to_normal_1d():
    MEAN = 10
    UNCERTAINTY = 10
    CONFIDENCE_INTERVAL = 95
    result = plus_minus_uncertainty_to_normal_1d(SHAPE, MEAN, UNCERTAINTY, CONFIDENCE_INTERVAL)
    assert_rows_identical(result)
    assert result.shape == SHAPE


def test_plus_minus_uncertainty_to_normal_2d():
    MEAN = 10
    UNCERTAINTY = 10
    CONFIDENCE_INTERVAL = 95
    result = plus_minus_uncertainty_to_normal_2d(SHAPE, MEAN, UNCERTAINTY, CONFIDENCE_INTERVAL)
    assert_rows_unique(result)
    assert result.shape == SHAPE


def test_grouped_avg():
    INPUT = array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12],
        [13, 14, 15],
        [16, 17, 18]
    ])
    EXPECTED = array([
        [4, 5, 6],
        [13, 14, 15]
    ])
    result = grouped_avg(INPUT, n=3)
    assert_array_equal(result, EXPECTED)


def test_avg_run_in_columnwise():
    INPUT = array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12],
        [13, 14, 15],
        [16, 17, 18]
    ])
    EXPECTED = array([
        [4, 5, 6],
        [10, 11, 12],
        [13, 14, 15],
        [16, 17, 18]
    ])
    result = avg_run_in_columnwise(INPUT, n=3)
    assert_array_equal(result, EXPECTED)


def test_avg_run_in_rowwise():
    INPUT = array([
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15]
    ])
    EXPECTED = array([
        [2, 4, 5],
        [7, 9, 10],
        [12, 14, 15]
    ])
    result = avg_run_in_rowwise(INPUT, n=3)
    assert_array_equal(result, EXPECTED)


def test_gen_seed():
    NODE = {"@id": "site"}
    EXPECTED = 1209943397
    result = gen_seed(NODE, "model", "term")
    assert result == EXPECTED


def test_gen_seed_no_id():
    NODE = {}
    EXPECTED = 2140941220
    result = gen_seed(NODE)
    assert result == EXPECTED


# means, sds, correlation_matrix, tol_kwargs
PARAMS_CORRELATED_NORMAL_2D = [
    (
        array([0, 0, 0, 0, 0]),
        array([1, 1, 1, 1, 1]),
        array([
            [1.0, 0.5, 0.25, 0.125, 0.0625],
            [0.5, 1.0, 0.5, 0.25, 0.125],
            [0.25, 0.5, 1.0, 0.5, 0.25],
            [0.125, 0.25, 0.5, 1.0, 0.5],
            [0.0625, 0.125, 0.25, 0.5, 1.0]
        ]),
        {"atol": 0.05}
    ),
    (
        array([40000, 42000, 43000, 44333.333]),
        array([4000, 4200, 4300, 4433.333]),
        array([
            [1.0, 0.965867, 0.932987, 0.901227],
            [0.965867, 1.0, 0.965959, 0.933076],
            [0.932987, 0.965959, 1.0, 0.965959],
            [0.901227, 0.933076, 0.965959, 1.0]
        ]),
        {"rtol": 0.05}
    ),
    (
        array([40000, 42000, 43000, 44333.333]),
        array([4000, 4200, 4300, 4433.333]),
        array([
            [1.0, 0, 0, 0],
            [0, 1.0, 0, 0],
            [0, 0, 1.0, 0],
            [0, 0, 0, 1.0]
        ]),
        {"rtol": 0.05}
    )
]
IDS_CORRELATED_NORMAL_2D = [
    "standard normal distributions",
    "custom normal distributions",
    "no correlation"
]


@mark.parametrize(
    "means, sds, correlation_matrix, tol_kwargs",
    PARAMS_CORRELATED_NORMAL_2D,
    ids=IDS_CORRELATED_NORMAL_2D
)
def test_correlated_normal_2d_standard_normal_dist(
    means: NDArray, sds: NDArray, correlation_matrix: NDArray, tol_kwargs: dict
):
    result = correlated_normal_2d(N_ITERATIONS, means, sds, correlation_matrix, seed=SEED)
    empirical_correlation_matrix = corrcoef(result)

    assert_allclose(result.mean(axis=1), means, **tol_kwargs)  # row-wise mean matches input
    assert_allclose(result.std(axis=1), sds, **tol_kwargs)  # row-wise SD matches input
    assert_allclose(empirical_correlation_matrix, correlation_matrix, atol=0.05)  # correlation matches input
