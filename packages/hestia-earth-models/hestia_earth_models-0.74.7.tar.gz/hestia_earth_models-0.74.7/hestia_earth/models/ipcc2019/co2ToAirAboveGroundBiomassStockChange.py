from hestia_earth.schema import EmissionMethodTier, MeasurementMethodClassification

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission

from .biomass_utils import detect_land_cover_change, get_valid_management_nodes, summarise_land_cover_nodes
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
                    "term.@id": "aboveGroundBiomass"
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
        "methodTier": ""
    }]
}
TERM_ID = 'co2ToAirAboveGroundBiomassStockChangeLandUseChange,co2ToAirAboveGroundBiomassStockChangeManagementChange'

_LU_EMISSION_TERM_ID = "co2ToAirAboveGroundBiomassStockChangeLandUseChange"
_MG_EMISSION_TERM_ID = "co2ToAirAboveGroundBiomassStockChangeManagementChange"

_CARBON_STOCK_TERM_ID = 'aboveGroundBiomass'

_MEASUREMENT_METHOD_RANKING = [
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS,
    MeasurementMethodClassification.TIER_3_MODEL,
    MeasurementMethodClassification.TIER_2_MODEL,
    MeasurementMethodClassification.TIER_1_MODEL,
    MeasurementMethodClassification.GEOSPATIAL_DATASET
]
"""
The list of `MeasurementMethodClassification`s that can be used to calculate SOC stock change emissions, ranked in
order from strongest to weakest.
"""


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
    }
    emission = _new_emission(term_id, MODEL) | {
        key: value for key, value in update_dict.items() if value
    }
    return emission


def run(cycle: dict) -> list[dict]:
    """
    Run the `ipcc2019.co2ToAirAboveGroundBiomassStockChangeManagementChange`.

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
        measurements_mandatory=False,  # Model can allocate zero emissions to LUC with enough landCover data
        measurement_method_ranking=_MEASUREMENT_METHOD_RANKING,
        get_valid_management_nodes_func=get_valid_management_nodes,
        summarise_land_use_func=summarise_land_cover_nodes,
        detect_land_use_change_func=detect_land_cover_change,
    )

    run_exec = create_run_function(
        new_emission_func=_emission,
        land_use_change_emission_term_id=_LU_EMISSION_TERM_ID,
        management_change_emission_term_id=_MG_EMISSION_TERM_ID
    )

    should_run, cycle_id, inventory, logs = should_run_exec(cycle)

    for term_id in [_LU_EMISSION_TERM_ID, _MG_EMISSION_TERM_ID]:
        logRequirements(cycle, model=MODEL, term=term_id, **logs)
        logShouldRun(cycle, MODEL, term_id, should_run)

    return run_exec(cycle_id, inventory) if should_run else []
