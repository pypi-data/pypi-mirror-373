from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.date import YEAR

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission

from .co2ToAirCarbonStockChange_utils import create_run_function, create_should_run_function
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "measurements": [
                {
                    "@type": "Measurement",
                    "value": "",
                    "dates": "",
                    "depthUpper": "0",
                    "depthLower": "30",
                    "term.@id": "biocharOrganicCarbonPerHa"
                }
            ]
        },
        "functionalUnit": "1 ha",
        "endDate": "",
        "optional": {
            "startDate": ""
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "statsDefinition": "simulated",
        "observations": "",
        "methodTier": "",
        "depth": 30
    }]
}
TERM_ID = 'co2ToAirBiocharStockChange'

_DEPTH_UPPER = 0
_DEPTH_LOWER = 30

_CARBON_STOCK_TERM_ID = 'biocharOrganicCarbonPerHa'

_TRANSITION_PERIOD_YEARS = 100
_TRANSITION_PERIOD_DAYS = _TRANSITION_PERIOD_YEARS * YEAR

_EXCLUDE_FROM_LOGS = ["land_use_inventory"]  # not required for model


def _emission(
    *,
    term_id: str,
    value: list[float],
    method_tier: EmissionMethodTier,
    sd: list[float] = None,
    min: list[float] = None,
    max: list[float] = None,
    statsDefinition: str = None,
    observations: list[int] = None
) -> dict:
    """
    Create an emission node based on the provided value and method tier.

    See [Emission schema](https://www.hestia.earth/schema/Emission) for more information.

    Parameters
    ----------
    value : float
        The emission value (kg CO2 ha-1).
    sd : float
        The standard deviation (kg CO2 ha-1).
    method_tier : EmissionMethodTier
        The emission method tier.

    Returns
    -------
    dict
        The emission dictionary with keys 'depth', 'value', and 'methodTier'.
    """
    update_dict = {
        "value": value,
        "sd": sd,
        "min": min,
        "max": max,
        "statsDefinition": statsDefinition,
        "observations": observations,
        "methodTier": method_tier.value,
        "depth": _DEPTH_LOWER
    }
    emission = _new_emission(term_id, MODEL) | {
        key: value for key, value in update_dict.items() if value
    }
    return emission


def run(cycle: dict) -> list[dict]:
    """
    Run the `ipcc2019.co2ToAirBelowGroundBiomassStockChangeManagementChange`.

    Parameters
    ----------
    cycle : dict
        A HESTIA (Cycle node)[https://www.hestia.earth/schema/Cycle].

    Returns
    -------
    list[dict]
        A list of [Emission nodes](https://www.hestia.earth/schema/Emission) containing model results.
    """
    should_run_exec = create_should_run_function(
        _CARBON_STOCK_TERM_ID,
        depth_upper=_DEPTH_UPPER,
        depth_lower=_DEPTH_LOWER,
        transition_period=_TRANSITION_PERIOD_DAYS
    )

    run_exec = create_run_function(
        new_emission_func=_emission,
        land_use_change_emission_term_id=None,  # All emissions allocated to management change
        management_change_emission_term_id=TERM_ID
    )

    should_run, cycle_id, inventory, logs = should_run_exec(cycle)

    logRequirements(
        cycle,
        model=MODEL,
        term=TERM_ID,
        **{k: v for k, v in logs.items() if k not in _EXCLUDE_FROM_LOGS}
    )
    logShouldRun(cycle, MODEL, TERM_ID, should_run)

    return run_exec(cycle_id, inventory) if should_run else []
