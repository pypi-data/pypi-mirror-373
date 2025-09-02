from numpy import array, e, inf
from numpy.typing import NDArray
from numpy.testing import assert_almost_equal
from hestia_earth.utils.date import YEAR
from hestia_earth.models.utils.time_series import (
    calc_tau, compute_time_series_correlation_matrix, exponential_decay
)

from pytest import mark


SEED = 0
N_ITERATIONS = 10000


# datestrs, half_life, expected
PARAMS_COMPUTE_CORRELATION_MATRIX = [
    (
        ['2000-01-01', '2000-01-02', '2000-01-03', '2000-01-04', '2000-01-05'],
        1,
        array([
            [1.0, 0.5, 0.25, 0.125, 0.0625],
            [0.5, 1.0, 0.5, 0.25, 0.125],
            [0.25, 0.5, 1.0, 0.5, 0.25],
            [0.125, 0.25, 0.5, 1.0, 0.5],
            [0.0625, 0.125, 0.25, 0.5, 1.0]
        ])
    ),
    (
        ['2000-01-01', '2001-01-01', '2002-01-01', '2003-01-01'],
        20*YEAR,
        array([
            [1.0, 0.965867, 0.932987, 0.901227],
            [0.965867, 1.0, 0.965959, 0.933076],
            [0.932987, 0.965959, 1.0, 0.965959],
            [0.901227, 0.933076, 0.965959, 1.0]
        ])
    )
]
IDS_COMPUTE_CORRELATION_MATRIX = [
    "dt: 1d, half-life: 1d",
    "dt: 1y, half-life: 20y"
]


@mark.parametrize(
    "datestrs, half_life, expected",
    PARAMS_COMPUTE_CORRELATION_MATRIX,
    ids=IDS_COMPUTE_CORRELATION_MATRIX
)
def test_compute_time_series_correlation_matrix(datestrs: list[str], half_life: float, expected: NDArray):
    tau = calc_tau(half_life)
    result = compute_time_series_correlation_matrix(
        datestrs,
        decay_fn=lambda dt: exponential_decay(dt, tau=tau)
    )

    assert_almost_equal(result, expected, decimal=6)


# half_life, expected
PARAMS_CALC_TAU = [(0.693147, 1), (1, 1.442695), (20, 28.853901), (YEAR, 526.933543)]
IDS_CALC_TAU = [half_life for half_life, *_ in PARAMS_CALC_TAU]


@mark.parametrize("half_life, expected", PARAMS_CALC_TAU, ids=IDS_CALC_TAU)
def test_calc_tau(half_life: float, expected: float):
    result = calc_tau(half_life)
    assert_almost_equal(result, expected, decimal=6)


PARAMS_EXPONENTIAL_DECAY = [
    (0, 1, 1, 0, 1),
    (1, 1, 1, 0, e ** -1),
    (inf, 1, 1, 0, 0),
    (YEAR, calc_tau(YEAR), 1.5, -3, -0.75)  # 1 year w/ half-life = 1 year and custom min/max
]
IDS_EXPONENTIAL_DECAY = [f"t: {t:0.2f}, tau: {tau:0.2f}" for t, tau, *_ in PARAMS_EXPONENTIAL_DECAY]


@mark.parametrize(
    "t, tau, initial_value, final_value, expected",
    PARAMS_EXPONENTIAL_DECAY,
    ids=IDS_EXPONENTIAL_DECAY
)
def test_exponential_decay(t: float, tau: float, initial_value: float, final_value: float, expected: float):
    result = exponential_decay(t, tau, initial_value, final_value)
    assert_almost_equal(result, expected, decimal=6)
