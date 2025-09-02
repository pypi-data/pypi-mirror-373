from hestia_earth.utils.date import diff_in_days

from itertools import product
from numpy import array, exp, log
from numpy.typing import NDArray
from typing import Callable


def exponential_decay(t: float, tau: float = 1, initial_value: float = 1, final_value: float = 0) -> float:
    """
    Calculate the exponentially decaying value based on the time elapsed.

    Parameters
    ----------
    t : float
        The time elapsed.
    tau : float, optional
        The decay constant, related to the half-life (default = 1).
    initial_value : float, optional
        The value at time t = 0 (default = 1).
    final_value : float, optional
        The value as time approaches infinity (default = 0).

    Returns
    -------
    float
        The exponentially decaying value based on the given parameters.
    """
    return final_value + (initial_value - final_value) * exp(-t / tau)


def calc_tau(half_life: float) -> float:
    """
    Calculate the decay constant (tau) for an exponential_decay function from the half-life.

    Parameters
    ----------
    half_life : float
        The half-life period over which the value transitions to half its initial value.

    Returns
    -------
    float
        The decay constant tau corresponding to the specified half-life.
    """
    return half_life / log(2)


def compute_time_series_correlation_matrix(
    datestrs: list[str],
    delta_time_fn: Callable[[str, str], float] = diff_in_days,
    decay_fn: Callable[[float], float] = exponential_decay
) -> NDArray:
    """
    Computes a correlation matrix for a list of time points (dates). Correlations decay as the time difference between
    dates increases. The time difference calculation and the decay function can be customized.

    n.b. The default decay function produces correlations between 0 and 1. Alternative decay functions may allow for
    negative correlations, giving values between -1 and 1.

    n.b. The function assumes that the `delta_time_fn` and `decay_fn` are appropriate for the format of the provided
    date strings.

    Parameters
    ----------
    datestrs : list[str]
        List of date strings representing time points in the time series.

    delta_time_fn : Callable[[str, str], float], optional
        Function to calculate the time difference between two date strings. Defaults to `diff_in_days`, which returns
        the difference in days. The function must have the following signature `f(date_1: str, date_2: str) -> float`.

    decay_fn : Callable[[float], float], optional
        Function to apply decay to the time differences. Defaults to `exponential_decay`, which models an exponential
        decay in correlation. The function must have the following signature `f(delta_time: float) -> float`.

    Returns
    -------
    NDArray
        A symmetric 2D array with shape `(len(datestrs), len(datestrs))` containing correlation values between time
        points, with all values between -1 and 1.
    """
    n_dates = len(datestrs)

    correlation_matrix = array([
        decay_fn(abs(delta_time_fn(date_1, date_2)))
        for date_1, date_2 in product(datestrs, repeat=2)
    ]).reshape(n_dates, n_dates)

    return correlation_matrix
