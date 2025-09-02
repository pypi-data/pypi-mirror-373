import numpy as np
import numpy.typing as npt
from typing import Callable, Union
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.stats import gen_seed, repeat_single, truncated_normal_1d
from hestia_earth.utils.descriptive_stats import calc_descriptive_stats

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.cycle import land_occupation_per_ha
from hestia_earth.models.utils.ecoClimateZone import EcoClimateZone, get_eco_climate_zone_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.site import valid_site_type

from .organicSoilCultivation_utils import (
    assign_organic_soil_category, calc_emission, format_nd_array, format_number, get_emission_factor,
    OrganicSoilCategory, valid_eco_climate_zone
)
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": [
            {
                "cycleDuration": "",
                "practices": [{"@type": "Practice", "value": "", "term.@id": "longFallowRatio"}]
            },
            {
                "@doc": "for plantations, additional properties are required",
                "practices": [
                    {"@type": "Practice", "value": "", "term.@id": "nurseryDensity"},
                    {"@type": "Practice", "value": "", "term.@id": "nurseryDuration"},
                    {"@type": "Practice", "value": "", "term.@id": "plantationProductiveLifespan"},
                    {"@type": "Practice", "value": "", "term.@id": "plantationDensity"},
                    {"@type": "Practice", "value": "", "term.@id": "plantationLifespan"},
                    {"@type": "Practice", "value": "", "term.@id": "rotationDuration"}
                ]
            }
        ],
        "site": {
            "@type": "Site",
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "histosol"},
                {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}
            ]
        },
        "optional": {
            "cycleDuration": ""
        }
    }
}
LOOKUPS = {
    "crop": [
        "isPlantation",
        "IPCC_2013_ORGANIC_SOIL_CULTIVATION_CATEGORY"
    ],
    "forage": [
        "isPlantation",
        "IPCC_2013_ORGANIC_SOIL_CULTIVATION_CATEGORY"
    ],
    "ecoClimateZone": [
        "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_ANNUAL_CROPS",
        "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_PERENNIAL_CROPS",
        "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_ACACIA",
        "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_OIL_PALM",
        "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_SAGO_PALM",
        "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_PADDY_RICE_CULTIVATION",
        "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_GRASSLAND",
        "IPCC_2013_ORGANIC_SOILS_TONNES_CO2-C_HECTARE_OTHER"
    ]
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "observations": "",
        "statsDefinition": "simulated",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'co2ToAirOrganicSoilCultivation'
TIER = EmissionMethodTier.TIER_1.value

_STATS_DEFINITION = EmissionStatsDefinition.SIMULATED.value
_ITERATIONS = 100000


def _emission(descriptive_stats: dict):
    emission = _new_emission(TERM_ID, MODEL) | descriptive_stats
    emission['methodTier'] = TIER
    return emission


def sample_emission_factor(
    eco_climate_zone: EcoClimateZone,
    organic_soil_category: OrganicSoilCategory,
    seed: Union[int, np.random.Generator, None] = None,
) -> npt.NDArray:
    factor_data = get_emission_factor(TERM_ID, eco_climate_zone, organic_soil_category)
    sample_func = _get_sample_func(factor_data)
    return sample_func(iterations=_ITERATIONS, seed=seed, **factor_data)


def _sample_truncated_normal(
    *, iterations: int, value: float, sd: float, seed: Union[int, np.random.Generator, None] = None, **_
) -> npt.NDArray:
    """
    Randomly sample a model parameter with a truncated normal distribution. Emission factors annot be below 0, so
    truncated normal sampling used.
    """
    return truncated_normal_1d(shape=(1, iterations), mu=value, sigma=sd, low=0, high=np.inf, seed=seed)


def _sample_constant(*, value: float, **_) -> npt.NDArray:
    """Sample a constant model parameter."""
    return repeat_single(shape=(1, 1), value=value)


_KWARGS_TO_SAMPLE_FUNC = {
    ("value", "sd"): _sample_truncated_normal,
    ("value",): _sample_constant
}
"""
Mapping from available distribution data to sample function.
"""


def _get_sample_func(kwargs: dict) -> Callable:
    """
    Select the correct sample function for a parameter based on the distribution data available. All possible
    parameters for the model should have, at a minimum, a `value`, meaning that no default function needs to be
    specified.

    This function has been extracted into it's own method to allow for mocking of sample function.

    Keyword Args
    ------------
    value : float
        The distribution mean.
    sd : float
        The standard deviation of the distribution.
    se : float
        The standard error of the distribution.
    n : float
        Sample size.

    Returns
    -------
    Callable
        The sample function for the distribution.
    """
    return next(
        sample_func for required_kwargs, sample_func in _KWARGS_TO_SAMPLE_FUNC.items()
        if all(kwarg in kwargs.keys() for kwarg in required_kwargs)
    )


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])

    seed = gen_seed(cycle, MODEL, TERM_ID)
    rng = np.random.default_rng(seed)

    def _get_measurement_content(term_id: str):
        return most_relevant_measurement_value(measurements, term_id, end_date)

    histosol = _get_measurement_content('histosol')
    eco_climate_zone = get_eco_climate_zone_value(cycle, as_enum=True)
    organic_soil_category = assign_organic_soil_category(cycle, log_id=TERM_ID)

    emission_factor = (
        sample_emission_factor(eco_climate_zone, organic_soil_category, seed=rng) if eco_climate_zone
        else None
    )
    land_occupation = land_occupation_per_ha(MODEL, TERM_ID, cycle)

    logRequirements(
        cycle, model=MODEL, term=TERM_ID,
        eco_climate_zone=eco_climate_zone,
        organic_soil_category=organic_soil_category,
        emission_factor=format_nd_array(emission_factor),
        land_occupation=format_number(land_occupation),
        histosol=format_number(histosol)
    )

    should_run = all([
        valid_site_type(site),
        valid_eco_climate_zone(eco_climate_zone),
        all(
            var is not None for var in [
                emission_factor,
                land_occupation,
                histosol
            ]
        )
    ])

    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)

    return should_run, emission_factor, histosol, land_occupation


def _run(emission_factor: npt.NDArray, histosol: float, land_occupation: float):
    result = calc_emission(TERM_ID, emission_factor, histosol, land_occupation)
    descriptive_stats = calc_descriptive_stats(result, _STATS_DEFINITION)
    return [_emission(descriptive_stats)]


def run(cycle: dict):
    should_run, emission_factor, histosol, land_occupation = _should_run(cycle)
    return _run(emission_factor, histosol, land_occupation) if should_run else []
