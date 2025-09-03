from enum import Enum
from numpy import array, empty, exp, minimum, random, where, vstack
from numpy.typing import NDArray
from pydash.objects import merge
from typing import Any, Callable, Union
from hestia_earth.schema import (
    CycleFunctionalUnit, MeasurementMethodClassification, SiteSiteType, TermTermType
)
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list
from hestia_earth.utils.blank_node import get_node_value
from hestia_earth.utils.stats import (
    avg_run_in_columnwise, gen_seed, grouped_avg, repeat_1d_array_as_columns
)
from hestia_earth.utils.descriptive_stats import calc_descriptive_stats

from hestia_earth.models.utils.blank_node import (
    cumulative_nodes_lookup_match, cumulative_nodes_term_match, group_nodes_by_year, group_nodes_by_year_and_month,
    GroupNodesByYearMode, node_lookup_match, node_term_match
)
from hestia_earth.models.utils.cycle import check_cycle_site_ids_identical
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.site import related_cycles
from hestia_earth.models.utils.term import get_upland_rice_crop_terms, get_upland_rice_land_cover_terms

from .organicCarbonPerHa_utils import (
    CarbonSource, check_consecutive, DEPTH_LOWER, DEPTH_UPPER, check_irrigation,
    IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE, IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE,
    IpccLandUseCategory, IpccManagementCategory, is_cover_crop, MIN_AREA_THRESHOLD, MIN_YIELD_THRESHOLD,
    sample_constant, sample_plus_minus_uncertainty, sample_truncated_normal, STATS_DEFINITION
)
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "siteType": "cropland",
        "measurements": [
            {
                "@type": "Measurement",
                "term.@id": "sandContent",
                "value": "",
                "depthUpper": "0",
                "depthLower": "30",
                "optional": {
                    "dates": ""
                }
            },
            {
                "@type": "Measurement",
                "term.@id": "temperatureMonthly",
                "value": "",
                "dates": ""
            },
            {
                "@type": "Measurement",
                "term.@id": "precipitationMonthly",
                "value": "",
                "dates": ""
            },
            {
                "@type": "Measurement",
                "term.@id": "potentialEvapotranspirationMonthly",
                "value": "",
                "dates": ""
            }
        ],
        "related": {
            "Cycle": [{
                "endDate": "",
                "products": [
                    {
                        "@type": "Product",
                        "term.@id": [
                            "aboveGroundCropResidueLeftOnField",
                            "aboveGroundCropResidueIncorporated",
                            "belowGroundCropResidue",
                            "discardedCropLeftOnField",
                            "discardedCropIncorporated"
                        ],
                        "value": "",
                        "properties": [
                            {
                                "@type": "Property",
                                "term.@id": "carbonContent",
                                "value": ""
                            },
                            {
                                "@type": "Property",
                                "term.@id": "nitrogenContent",
                                "value": ""
                            },
                            {
                                "@type": "Property",
                                "term.@id": "ligninContent",
                                "value": ""
                            }
                        ]
                    }
                ],
                "inputs": [
                    {
                        "@type": "Input",
                        "term.termType": ["organicFertiliser", "soilAmendment"],
                        "value": "",
                        "properties": [
                            {
                                "@type": "Property",
                                "term.@id": "carbonContent",
                                "value": ""
                            },
                            {
                                "@type": "Property",
                                "term.@id": "nitrogenContent",
                                "value": ""
                            },
                            {
                                "@type": "Property",
                                "term.@id": "ligninContent",
                                "value": ""
                            }
                        ]
                    }
                ],
                "practices": [
                    {
                        "@type": "Practice",
                        "term.termType": "tillage",
                        "value": ""
                    },
                    {
                        "@type": "Practice",
                        "term.termType": "waterRegime",
                        "name": "irrigated",
                        "value": "",
                        "startDate": "",
                        "endDate": ""
                    }
                ],
                "optional": {
                    "startDate": ""
                }
            }]
        }
    }
}
LOOKUPS = {
    "crop": "IPCC_LAND_USE_CATEGORY",
    "landCover": "IPCC_LAND_USE_CATEGORY",
    "tillage": "IPCC_TILLAGE_MANAGEMENT_CATEGORY"
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "statsDefinition": "simulated",
        "observations": "",
        "dates": "",
        "depthUpper": "0",
        "depthLower": "30",
        "methodClassification": "tier 2 model"
    }]
}

TERM_ID = 'organicCarbonPerHa'
_METHOD_CLASSIFICATION = MeasurementMethodClassification.TIER_2_MODEL.value

_RUN_IN_PERIOD = 5

_SAND_CONTENT_TERM_ID = "sandContent"
_NUMBER_OF_TILLAGES_TERM_ID = "numberOfTillages"
_TEMPERATURE_MONTHLY_TERM_ID = "temperatureMonthly"
_PRECIPITATION_MONTHLY_TERM_ID = "precipitationMonthly"
_PET_MONTHLY_TERM_ID = "potentialEvapotranspirationMonthly"
_ABOVE_GROUND_CROP_RESIDUE_TOTAL_TERM_ID = "aboveGroundCropResidueTotal"
_CARBON_CONTENT_TERM_ID = "carbonContent"
_NITROGEN_CONTENT_TERM_ID = "nitrogenContent"
_LIGNIN_CONTENT_TERM_ID = "ligninContent"
_DRY_MATTER_TERM_ID = "dryMatter"

_CROP_RESIDUE_MANAGEMENT_TERM_IDS = [
    "residueIncorporated",
    "residueIncorporatedLessThan30DaysBeforeCultivation",
    "residueIncorporatedMoreThan30DaysBeforeCultivation",
    "residueLeftOnField"
]

_CARBON_SOURCE_TERM_IDS = [
    "discardedCropIncorporated",
    "discardedCropLeftOnField",
    "belowGroundCropResidue",
]

_MIN_RESIDUE_LEFT_ON_FIELD = 20  # TODO: Confirm assumption
_DEFAULT_COVER_CROP_BIOMASS = 4000  # TODO: Confirm assumption, Source PAS 2050-1:2012

_CARBON_INPUT_PROPERTY_TERM_IDS = [
    _CARBON_CONTENT_TERM_ID,
    _NITROGEN_CONTENT_TERM_ID,
    _LIGNIN_CONTENT_TERM_ID,
    _DRY_MATTER_TERM_ID
]

_INPUT_CARBON_SOURCE_TERM_TYPES = [
    TermTermType.ORGANICFERTILISER.value,
    TermTermType.SOILAMENDMENT.value
]

_PRACTICE_CARBON_SOURCE_TERM_TYPES = [
    TermTermType.LANDCOVER
]

_PRODUCT_CARBON_SOURCE_TERM_TYPES = [
    TermTermType.CROPRESIDUE
]

_VALID_SITE_TYPES = [
    SiteSiteType.CROPLAND.value
]

_VALID_FUNCTIONAL_UNITS = [
    CycleFunctionalUnit._1_HA.value
]


def _measurement(
    timestamps: list[int],
    descriptive_stats_dict: dict
) -> dict:
    """
    Build a HESTIA `Measurement` node to contain a value and descriptive statistics calculated by the models.

    The `descriptive_stats_dict` parameter should include the following keys and values from the
    [Measurement](https://hestia.earth/schema/Measurement) schema:
    ```
    {
        "value": list[float],
        "sd": list[float],
        "min": list[float],
        "max": list[float],
        "statsDefinition": str,
        "observations": list[int]
    }
    ```

    Parameters
    ----------
    timestamps : list[int]
        A list of calendar years associated to the calculated SOC stocks.
    descriptive_stats_dict : dict
        A dict containing the descriptive statistics data that should be added to the node.

    Returns
    -------
    dict
        A valid HESTIA `Measurement` node, see: https://www.hestia.earth/schema/Measurement.
    """
    measurement = _new_measurement(TERM_ID, MODEL) | descriptive_stats_dict
    measurement["dates"] = [f"{year}-12-31" for year in timestamps]
    measurement["depthUpper"] = DEPTH_UPPER
    measurement["depthLower"] = DEPTH_LOWER
    measurement["methodClassification"] = _METHOD_CLASSIFICATION
    return measurement


class _InventoryKey(Enum):
    """
    Enum representing the inner keys of the annual inventory is constructed from site and cycle data.
    """
    TEMP_MONTHLY = 'temperature-monthly'
    PRECIP_MONTHLY = 'precipitation-monthly'
    PET_MONTHLY = 'pet-monthly'
    IRRIGATED_MONTHLY = 'irrigated-monthly'
    CARBON_INPUT = 'carbon-input'
    N_CONTENT = 'nitrogen-content'
    LIGNIN_CONTENT = 'lignin-content'
    TILLAGE_CATEGORY = 'ipcc-tillage-category'
    SAND_CONTENT = 'sand-content'
    IS_PADDY_RICE = 'is-paddy-rice'
    SHOULD_RUN = 'should-run-tier-2'


_REQUIRED_KEYS = {
    _InventoryKey.TEMP_MONTHLY,
    _InventoryKey.PRECIP_MONTHLY,
    _InventoryKey.PET_MONTHLY,
    _InventoryKey.CARBON_INPUT,
    _InventoryKey.N_CONTENT,
    _InventoryKey.LIGNIN_CONTENT,
    _InventoryKey.TILLAGE_CATEGORY,
    _InventoryKey.IS_PADDY_RICE
}
"""
The `_InventoryKey`s that must have valid values for an inventory year to be included in the model.
"""


class _Parameter(Enum):
    """
    The default Tier 2 model parameters provided in the IPCC (2019) report.
    """
    ACTIVE_DECAY_FACTOR = {
        "value": 7.4,
        "min": 7.4,
        "max": 7.4,
        "sd": 0
    }
    SLOW_DECAY_FACTOR = {
        "value": 0.209,
        "min": 0.058,
        "max": 0.3,
        "sd": 0.566
    }
    PASSIVE_DECAY_FACTOR = {
        "value": 0.00689,
        "min": 0.005,
        "max": 0.01,
        "sd": 0.00125
    }
    F_1 = {
        "value": 0.378,
        "min": 0.01,
        "max": 0.8,
        "sd": 0.0719
    }
    F_2_FULL_TILLAGE = {
        "value": 0.455,
        # No stats available in IPCC excel document.
    }
    F_2_REDUCED_TILLAGE = {
        "value": 0.477
        # No stats available in IPCC excel document.
    }
    F_2_NO_TILLAGE = {
        "value": 0.5
        # No stats available in IPCC excel document.
    }
    F_2_UNKNOWN_TILLAGE = {
        "value": 0.368,
        "min": 0.007,
        "max": 0.5,
        "sd": 0.0998
    }
    F_3 = {
        "value": 0.455,
        "min": 0.1,
        "max": 0.8,
        "sd": 0.201
    }
    F_5 = {
        "value": 0.0855,
        "min": 0.037,
        "max": 0.1,
        "sd": 0.0122
    }
    F_6 = {
        "value": 0.0504,
        "min": 0.02,
        "max": 0.19,
        "sd": 0.0280
    }
    F_7 = {
        "value": 0.42,
        "min": 0.42,
        "max": 0.42,
        "sd": 0
    }
    F_8 = {
        "value": 0.45,
        "min": 0.45,
        "max": 0.45,
        "sd": 0
    }
    TILLAGE_FACTOR_FULL_TILLAGE = {
        "value": 3.036,
        "min": 1.4,
        "max": 4.0,
        "sd": 0.579
    }
    TILLAGE_FACTOR_REDUCED_TILLAGE = {
        "value": 2.075,
        "min": 1.0,
        "max": 3.0,
        "sd": 0.569
    }
    TILLAGE_FACTOR_NO_TILLAGE = {
        "value": 1,
        "min": 1,
        "max": 1,
        "sd": 0
    }
    MAXIMUM_TEMPERATURE = {
        "value": 45,
        "min": 45,
        "max": 45,
        "sd": 0
    }
    OPTIMUM_TEMPERATURE = {
        "value": 33.69,
        "min": 30.7,
        "max": 35.34,
        "sd": 0.66
    }
    WATER_FACTOR_SLOPE = {
        "value": 1.331,
        "min": 0.8,
        "max": 2.0,
        "sd": 0.386
    }
    DEFAULT_CARBON_CONTENT = {
        "value": 0.42
        # No stats provided in IPCC report.
    }
    DEFAULT_NITROGEN_CONTENT = {
        "value": 0.0083,
        "uncertainty": 75
    }
    DEFAULT_LIGNIN_CONTENT = {
        "value": 0.073,
        "uncertainty": 50
    }


_PARAMETER_TO_SAMPLE_FUNCTION = {
    _Parameter.ACTIVE_DECAY_FACTOR: sample_constant,
    _Parameter.F_2_FULL_TILLAGE: sample_constant,
    _Parameter.F_2_REDUCED_TILLAGE: sample_constant,
    _Parameter.F_2_NO_TILLAGE: sample_constant,
    _Parameter.F_7: sample_constant,
    _Parameter.F_8: sample_constant,
    _Parameter.TILLAGE_FACTOR_NO_TILLAGE: sample_constant,
    _Parameter.MAXIMUM_TEMPERATURE: sample_constant,
    _Parameter.DEFAULT_CARBON_CONTENT: sample_constant,
    _Parameter.DEFAULT_NITROGEN_CONTENT: sample_plus_minus_uncertainty,
    _Parameter.DEFAULT_LIGNIN_CONTENT: sample_plus_minus_uncertainty
}
_DEFAULT_SAMPLE_FUNCTION = sample_truncated_normal


def _sample_parameter(
    iterations: int,
    parameter: _Parameter,
    seed: Union[int, random.Generator, None] = None
) -> NDArray:
    """
    Sample a model `_Parameter` using the function specified in `_PARAMETER_TO_SAMPLE_FUNCTION` or
    `_DEFAULT_SAMPLE_FUNCTION`.

    Parameters
    ----------
    iterations : int
        The number of samples to be taken.
    parameter : _Parameter
        The model parameter to be sampled.
    seed : int | Generator | None, optional
        A seed to initialize the BitGenerator. If passed a Generator, it will be returned unaltered. If `None`, then
        fresh, unpredictable entropy will be pulled from the OS.

    Returns
    -------
    NDArray
        A numpy array with shape `(1, iterations)`. All columns contain different sample values.
    """
    kwargs = parameter.value
    func = _get_sample_func(parameter)
    return func(iterations=iterations, seed=seed, **kwargs)


def _get_sample_func(parameter: _Parameter) -> Callable:
    """Extracted into method to allow for mocking of sample function."""
    return _PARAMETER_TO_SAMPLE_FUNCTION.get(parameter, _DEFAULT_SAMPLE_FUNCTION)


# --- TIER 2 MODEL ---


def should_run(site: dict) -> tuple[bool, dict, dict]:
    """
    Extract data from site & related cycles, pre-process data and determine whether there is sufficient data to run the
    Tier 2 model.

    The returned `inventory` should be a dict with the shape:
    ```
    {
        year (int): {
            _InventoryKey.SHOULD_RUN: bool,
            _InventoryKey.TEMP_MONTHLY: list[float],
            _InventoryKey.PRECIP_MONTHLY: list[float],
            _InventoryKey.PET_MONTHLY: list[float],
            _InventoryKey.IRRIGATED_MONTHLY: list[bool]
            _InventoryKey.CARBON_INPUT: float,
            _InventoryKey.N_CONTENT: float,
            _InventoryKey.TILLAGE_CATEGORY: IpccManagementCategory,
            _InventoryKey.SAND_CONTENT: float
        },
        ...
    }
    ```

    The returned `kwargs` should be a dict with the shape:
    ```
    {
        "sand_content": float
    }
    ```

    Parameters
    ----------
    site : dict
        A HESTIA `Site` node, see: https://www.hestia.earth/schema/Site.

    Returns
    -------
    tuple[bool, dict, dict]
        A tuple containing `(should_run_, inventory, kwargs)`.
    """
    site_type = site.get("siteType", "")
    measurement_nodes = site.get("measurements", [])
    cycles = related_cycles(site)

    has_measurements = len(measurement_nodes) > 0
    has_related_cycles = len(cycles) > 0
    has_functional_unit_1_ha = all(cycle.get("functionalUnit") in _VALID_FUNCTIONAL_UNITS for cycle in cycles)

    should_compile_inventory = all([
        site_type in _VALID_SITE_TYPES,
        has_measurements,
        has_related_cycles,
        check_cycle_site_ids_identical(cycles),
        has_functional_unit_1_ha
    ])

    inventory, kwargs = (
        _compile_inventory(cycles, measurement_nodes)
        if should_compile_inventory else ({}, {})
    )
    kwargs["seed"] = gen_seed(site, MODEL, TERM_ID)

    valid_years = [year for year, group in inventory.items() if group.get(_InventoryKey.SHOULD_RUN)]

    should_run_ = all([
        len(valid_years) >= _RUN_IN_PERIOD,
        check_consecutive(valid_years),
        any(inventory.get(year).get(_InventoryKey.SAND_CONTENT) for year in valid_years) or kwargs.get("sand_content")
    ])

    logs = {
        "site_type": site_type,
        "has_measurements": has_measurements,
        "has_related_cycles": has_related_cycles,
        "has_functional_unit_1_ha": has_functional_unit_1_ha,
        "should_compile_inventory_tier_2": should_compile_inventory,
        "should_run_tier_2": should_run_
    }

    return should_run_, inventory, kwargs, logs


def run(
    inventory: dict[int: dict[_InventoryKey: Any]],
    *,
    iterations: int,
    run_in_period: int = 5,
    sand_content: float = 0.33,
    seed: Union[int, random.Generator, None] = None,
    **_
) -> tuple[list[int], NDArray, NDArray, NDArray]:
    """
    Run the IPCC Tier 2 SOC model on a time series of annual data about a site and the mangagement activities taking
    place on it. To avoid any errors, the `inventory` parameter must be pre-validated by the `should_run` function.

    The inventory should be in the following shape:
    ```
    {
        year (int): {
            _InventoryKey.SHOULD_RUN: bool,
            _InventoryKey.TEMP_MONTHLY: list[float],
            _InventoryKey.PRECIP_MONTHLY: list[float],
            _InventoryKey.PET_MONTHLY: list[float],
            _InventoryKey.IRRIGATED_MONTHLY: list[bool]
            _InventoryKey.CARBON_INPUT: float,
            _InventoryKey.N_CONTENT: float,
            _InventoryKey.TILLAGE_CATEGORY: IpccManagementCategory,
            _InventoryKey.SAND_CONTENT: float
        },
        ...
    }
    ```

    TODO: interpolate between `sandContent` measurements for different years of the inventory

    Parameters
    ----------
    inventory : dict
        The inventory built by the `should_run` function.
    iterations : int
        Number of iterations to run the model for.
    run_in_period : int, optional
        The length of the run-in period in years, must be greater than or equal to 1. Default value: `5`.
    sand_content : float, optional
        A back-up sand content for if none are found in the inventory, decimal proportion. Default value: `0.33`.
    seed : int | Generator | None, optional
        A seed to initialize the BitGenerator. If passed a Generator, it will be returned unaltered. If `None`, then
        fresh, unpredictable entropy will be pulled from the OS.

    Returns
    -------
    list[dict]
        A list of HESTIA nodes containing model output results.
    """
    valid_inventory = {
        year: group for year, group in inventory.items() if group.get(_InventoryKey.SHOULD_RUN)
    }

    def _unpack_inventory(inventory_key: _InventoryKey, monthly: bool = False) -> NDArray:
        """
        Unpack the inventory dict into numpy arrays with the correct shape.
        """
        unpacked = [group[inventory_key] for group in valid_inventory.values()]
        arr = array(flatten(unpacked) if monthly else unpacked)
        return repeat_1d_array_as_columns(iterations, arr)

    timestamps = [year for year in valid_inventory.keys()]

    temperature_monthly = _unpack_inventory(_InventoryKey.TEMP_MONTHLY, monthly=True)
    precipitation_monthly = _unpack_inventory(_InventoryKey.PRECIP_MONTHLY, monthly=True)
    pet_monthly = _unpack_inventory(_InventoryKey.PET_MONTHLY, monthly=True)
    irrigated_monthly = _unpack_inventory(_InventoryKey.IRRIGATED_MONTHLY, monthly=True)

    carbon_input_annual = _unpack_inventory(_InventoryKey.CARBON_INPUT)
    n_content_annual = _unpack_inventory(_InventoryKey.N_CONTENT)
    lignin_content_annual = _unpack_inventory(_InventoryKey.LIGNIN_CONTENT)

    tillage_category_annual = [group[_InventoryKey.TILLAGE_CATEGORY] for group in valid_inventory.values()]

    sand_content = next(
        (
            group[_InventoryKey.SAND_CONTENT] for group in valid_inventory.values()
            if _InventoryKey.SAND_CONTENT in group
        ),
        sand_content
    )

    # --- SAMPLE PARAMETERS ---

    rng = random.default_rng(seed)

    active_decay_factor = _sample_parameter(iterations, _Parameter.ACTIVE_DECAY_FACTOR, seed=rng)
    slow_decay_factor = _sample_parameter(iterations, _Parameter.SLOW_DECAY_FACTOR, seed=rng)
    passive_decay_factor = _sample_parameter(iterations, _Parameter.PASSIVE_DECAY_FACTOR, seed=rng)
    f_1 = _sample_parameter(iterations, _Parameter.F_1, seed=rng)
    f_2_full_tillage = _sample_parameter(iterations, _Parameter.F_2_FULL_TILLAGE, seed=rng)
    f_2_reduced_tillage = _sample_parameter(iterations, _Parameter.F_2_REDUCED_TILLAGE, seed=rng)
    f_2_no_tillage = _sample_parameter(iterations, _Parameter.F_2_NO_TILLAGE, seed=rng)
    f_2_unknown_tillage = _sample_parameter(iterations, _Parameter.F_2_UNKNOWN_TILLAGE, seed=rng)
    f_3 = _sample_parameter(iterations, _Parameter.F_3, seed=rng)
    f_5 = _sample_parameter(iterations, _Parameter.F_5, seed=rng)
    f_6 = _sample_parameter(iterations, _Parameter.F_6, seed=rng)
    f_7 = _sample_parameter(iterations, _Parameter.F_7, seed=rng)
    f_8 = _sample_parameter(iterations, _Parameter.F_8, seed=rng)
    tillage_factor_full_tillage = _sample_parameter(iterations, _Parameter.TILLAGE_FACTOR_FULL_TILLAGE, seed=rng)
    tillage_factor_reduced_tillage = _sample_parameter(iterations, _Parameter.TILLAGE_FACTOR_REDUCED_TILLAGE, seed=rng)
    tillage_factor_no_tillage = _sample_parameter(iterations, _Parameter.TILLAGE_FACTOR_NO_TILLAGE, seed=rng)
    maximum_temperature = _sample_parameter(iterations, _Parameter.MAXIMUM_TEMPERATURE, seed=rng)
    optimum_temperature = _sample_parameter(iterations, _Parameter.OPTIMUM_TEMPERATURE, seed=rng)
    water_factor_slope = _sample_parameter(iterations, _Parameter.WATER_FACTOR_SLOPE, seed=rng)

    f_4 = _calc_f_4(sand_content, f_5)

    # --- CALCULATE TILLAGE AND CLIMATE FACTORS ---

    f_2_annual = _get_f_2_annual(
        tillage_category_annual, f_2_full_tillage, f_2_reduced_tillage, f_2_no_tillage, f_2_unknown_tillage
    )

    tillage_factor_annual = _get_tillage_factor_annual(
        tillage_category_annual, tillage_factor_full_tillage, tillage_factor_reduced_tillage, tillage_factor_no_tillage
    )

    temperature_factor_annual = _calc_temperature_factor_annual(
        temperature_monthly, maximum_temperature, optimum_temperature
    )

    water_factor_annual = _calc_water_factor_annual(
        precipitation_monthly, pet_monthly, irrigated_monthly, water_factor_slope
    )

    # --- AVERAGE RUN-IN YEARS TO STABILISE INITIAL SOC STOCK ---

    timestamps_ = timestamps[run_in_period - 1:]  # Last year of run in becomes first year of results.

    temperature_factors = avg_run_in_columnwise(temperature_factor_annual, run_in_period)
    water_factors = avg_run_in_columnwise(water_factor_annual, run_in_period)
    carbon_inputs = avg_run_in_columnwise(carbon_input_annual, run_in_period)
    n_contents = avg_run_in_columnwise(n_content_annual, run_in_period)
    lignin_contents = avg_run_in_columnwise(lignin_content_annual, run_in_period)
    f_2s = avg_run_in_columnwise(f_2_annual, run_in_period)
    tillage_factors = avg_run_in_columnwise(tillage_factor_annual, run_in_period)

    shape = temperature_factors.shape

    # --- CALCULATE THE ACTIVE ACTIVE POOL STEADY STATES ---

    alphas = _calc_alpha(
        carbon_inputs, f_2s, f_4, lignin_contents, n_contents, f_1, f_3, f_5, f_6, f_7, f_8
    )

    active_pool_decay_rates = _calc_active_pool_decay_rate(
        temperature_factors, water_factors, tillage_factors, sand_content, active_decay_factor
    )

    active_pool_steady_states = _calc_active_pool_steady_state(
        alphas, active_pool_decay_rates
    )

    # --- CALCULATE THE SLOW POOL STEADY STATES ---

    slow_pool_decay_rates = _calc_slow_pool_decay_rate(
        temperature_factors, water_factors, tillage_factors, slow_decay_factor
    )

    slow_pool_steady_states = _calc_slow_pool_steady_state(
        carbon_inputs, f_4, active_pool_steady_states, active_pool_decay_rates, slow_pool_decay_rates,
        lignin_contents, f_3
    )

    # --- CALCULATE THE PASSIVE POOL STEADY STATES ---

    passive_pool_decay_rates = _calc_passive_pool_decay_rate(
        temperature_factors, water_factors, passive_decay_factor
    )

    passive_pool_steady_states = _calc_passive_pool_steady_state(
        active_pool_steady_states, slow_pool_steady_states, active_pool_decay_rates, slow_pool_decay_rates,
        passive_pool_decay_rates, f_5, f_6
    )

    # --- CALCULATE THE ACTIVE, SLOW AND PASSIVE POOL SOC STOCKS ---

    active_pool_soc_stocks = empty(shape)
    slow_pool_soc_stocks = empty(shape)
    passive_pool_soc_stocks = empty(shape)

    active_pool_soc_stocks[0] = active_pool_steady_states[0]
    slow_pool_soc_stocks[0] = slow_pool_steady_states[0]
    passive_pool_soc_stocks[0] = passive_pool_steady_states[0]

    for index in range(1, len(timestamps_)):
        active_pool_soc_stocks[index] = _calc_sub_pool_soc_stock(
            active_pool_steady_states[index],
            active_pool_soc_stocks[index - 1],
            active_pool_decay_rates[index]
        )

        slow_pool_soc_stocks[index] = _calc_sub_pool_soc_stock(
            slow_pool_steady_states[index],
            slow_pool_soc_stocks[index - 1],
            slow_pool_decay_rates[index]
        )

        passive_pool_soc_stocks[index] = _calc_sub_pool_soc_stock(
            passive_pool_steady_states[index],
            passive_pool_soc_stocks[index - 1],
            passive_pool_decay_rates[index]
        )

    # --- ADD THE POOLS AND RETURN THE RESULT ---

    soc_stocks = active_pool_soc_stocks + slow_pool_soc_stocks + passive_pool_soc_stocks

    descriptive_stats = calc_descriptive_stats(
        soc_stocks,
        STATS_DEFINITION,
        axis=1,     # Calculate stats rowwise.
        decimals=6  # Round values to the nearest milligram.
    )

    return [_measurement(timestamps_, descriptive_stats)]


def _calc_temperature_factor_annual(
    temperature_monthly: NDArray,
    maximum_temperature: NDArray = array(45),
    optimum_temperature: NDArray = array(33.69)
) -> NDArray:
    """
    Equation 5.0E part 2, Temperature effect on decomposition for mineral soils using the steady-state method, Page
    5.22, Tier 2 Steady State Method for Mineral Soils, Chapter 5 Cropland, 2019 Refinement to the 2006 IPCC Guidelines
    for National Greenhouse Gas Inventories.

    Parameters
    ----------
        monthly_temperature : NDArray
            Monthly average air temprature, degrees C.
        maximum_temperature : NDArray
            Maximum monthly air temperature for decomposition, degrees C. Default value: `[45]`.
        optimum_temperature : NDArray
            Optimum air temperature for decomposition, degrees C. Default value: `[33.69]`.

    Returns
    -------
    NDArray
        Annual average air temperature effect on decomposition, dimensionless.
    """
    mask = temperature_monthly <= maximum_temperature
    prelim: NDArray = (maximum_temperature - temperature_monthly) / (maximum_temperature - optimum_temperature)

    temperature_factor_monthly = empty(temperature_monthly.shape)
    temperature_factor_monthly[mask] = pow(prelim[mask], 0.2) * exp((0.2 / 2.63) * (1 - pow(prelim[mask], 2.63)))
    temperature_factor_monthly[~mask] = 0

    return grouped_avg(temperature_factor_monthly, n=12)


def _calc_water_factor_annual(
    precipitation_monthly: NDArray,
    pet_monthly: NDArray,
    irrigated_monthly: NDArray = array(False),
    water_factor_slope: NDArray = array(1.331),
) -> NDArray:
    """
    Equation 5.0F, part 1. Calculate the average annual water effect on decomposition in mineral soils using the
    Steady-State Method multiplied by a coefficient of `1.5`.

    Parameters
    ----------
    precipitation_monthly : NDArray
        Monthly sum total precipitation, mm.
    pet_monthly : NDArray
        Monthly sum total potential evapotranspiration, mm.
    is_irrigated_monthly : NDArray
        Monthly true/false value that describe whether or not irrigation was used.
    water_factor_slope : NDArray
        The slope for mappet term to estimate water factor, dimensionless. Default value: `[1.331]`.

    Returns
    -------
    NDArray
        Annual water effect on decomposition, dimensionless.
    """
    MAX_MAPPET = 1.25
    WATER_FACTOR_IRRIGATED = 0.775

    shape = pet_monthly.shape
    mask = pet_monthly != 0

    mappet_monthly = empty(shape)
    mappet_monthly[mask] = minimum(precipitation_monthly[mask] / pet_monthly[mask], MAX_MAPPET)
    mappet_monthly[~mask] = MAX_MAPPET

    water_factor_monthly = where(
        irrigated_monthly,
        WATER_FACTOR_IRRIGATED,
        0.2129 + (water_factor_slope * mappet_monthly) - (0.2413 * mappet_monthly**2)
    )

    return 1.5 * grouped_avg(water_factor_monthly, n=12)


def _calc_f_4(sand_content: NDArray = array(0.33), f_5: NDArray = array(0.0855)) -> NDArray:
    """
    Equation 5.0C, part 4. Calculate the value of the stabilisation efficiencies for active pool decay products
    entering the slow pool based on the sand content of the soil.

    Parameters
    ----------
    sand_content : NDArray
        The sand content of the soil, decimal proportion. Default value: `[0.33]`.
    f_5 : NDArray
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal_proportion.
        Default value: `[0.0855]`.

    Returns
    -------
    NDArray
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    """
    return 1 - f_5 - (0.17 + 0.68 * sand_content)


def _get_f_2_annual(
    tillage_category_annual: list[IpccManagementCategory],
    f_2_full_tillage: NDArray = array(0.455),
    f_2_reduced_tillage: NDArray = array(0.477),
    f_2_no_tillage: NDArray = array(0.5),
    f_2_unknown_tillage: NDArray = array(0.368),
) -> NDArray:
    """
    Get the value of `f_2` (the stabilisation efficiencies for structural decay products entering the active pool)
    based on the tillage `IpccManagementCategory`.

    If tillage regime is unknown, `IpccManagementCategory.UNKNOWN` should be assumed.

    Parameters
    ----------
    tillage_category_annual : list[IpccManagementCategory]
        The tillage category for each year in the inventory.
    f_2_full_tillage : NDArray
        The stabilisation efficiencies for structural decay products entering the active pool under full tillage,
        decimal proportion. Default value: `[0.455]`.
    f_2_reduced_tillage : NDArray
        The stabilisation efficiencies for structural decay products entering the active pool under reduced tillage,
        decimal proportion. Default value: `[0.477]`.
    f_2_no_tillage : NDArray
        The stabilisation efficiencies for structural decay products entering the active pool under no tillage,
        decimal proportion. Default value: `[0.5]`.
    f_2_unknown_tillage : NDArray
        The stabilisation efficiencies for structural decay products entering the active pool if tillage is not known,
        decimal proportion. Default value: `[0.368]`.

    Returns
    -------
    NDArray
        The stabilisation efficiencies for structural decay products entering the active pool, decimal proportion.
    """
    ipcc_tillage_management_category_to_f_2s = {
        IpccManagementCategory.FULL_TILLAGE: f_2_full_tillage,
        IpccManagementCategory.REDUCED_TILLAGE: f_2_reduced_tillage,
        IpccManagementCategory.NO_TILLAGE: f_2_no_tillage,
        IpccManagementCategory.UNKNOWN: f_2_unknown_tillage
    }
    default = f_2_unknown_tillage
    return vstack([ipcc_tillage_management_category_to_f_2s.get(till, default) for till in tillage_category_annual])


def _get_tillage_factor_annual(
    tillage_category_annual: list[IpccManagementCategory],
    tillage_factor_full_tillage: NDArray = array(3.036),
    tillage_factor_reduced_tillage: NDArray = array(2.075),
    tillage_factor_no_tillage: NDArray = array(1)
) -> NDArray:
    """
    Calculate the tillage disturbance modifier on decay rate for active and slow sub-pools based on the tillage
    `IpccManagementCategory`.

    If tillage regime is unknown, `FULL_TILLAGE` should be assumed.

    Parameters
    ----------
    tillage_category_annual : list[IpccManagementCategory]
        The tillage category for each year in the inventory.
    tillage_factor_full_tillage : NDArray
        The tillage disturbance modifier for decay rates under full tillage, dimensionless. Default value: `[3.036]`.
    tillage_factor_reduced_tillage : NDArray
        Tillage disturbance modifier for decay rates under reduced tillage, dimensionless. Default value: `[2.075]`.
    tillage_factor_no_tillage : NDArray
        Tillage disturbance modifier for decay rates under no tillage, dimensionless. Default value: `[1]`.

    Returns
    -------
    NDArray
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    """
    ipcc_tillage_management_category_to_tillage_factors = {
        IpccManagementCategory.FULL_TILLAGE: tillage_factor_full_tillage,
        IpccManagementCategory.REDUCED_TILLAGE: tillage_factor_reduced_tillage,
        IpccManagementCategory.NO_TILLAGE: tillage_factor_no_tillage,
    }
    default = tillage_factor_full_tillage
    return vstack([
        ipcc_tillage_management_category_to_tillage_factors.get(till, default)
        for till in tillage_category_annual
    ])


def _calc_alpha(
    carbon_input: NDArray,
    f_2: NDArray,
    f_4: NDArray,
    lignin_content: NDArray = array(0.073),
    nitrogen_content: NDArray = array(0.0083),
    f_1: NDArray = array(0.378),
    f_3: NDArray = array(0.455),
    f_5: NDArray = array(0.0855),
    f_6: NDArray = array(0.0504),
    f_7: NDArray = array(0.42),
    f_8: NDArray = array(0.45)
) -> NDArray:
    """
    Equation 5.0G, part 1. Calculate the C input to the active soil carbon sub-pool, kg C ha-1.

    See table 5.5b for default values for lignin content and nitrogen content.

    Parameters
    ----------
    carbon_input : NDArray
        Total carbon input to the soil, kg C ha-1.
    f_2 : NDArray
        The stabilisation efficiencies for structural decay products entering the active pool, decimal proportion.
    f_4 : NDArray
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    lignin_content : NDArray
        The average lignin content of carbon input sources, decimal proportion. Default value: `[0.073]`.
    nitrogen_content : NDArray
        The average nitrogen content of carbon input sources, decimal proportion. Default value: `[0.0083]`.
    f_1 : NDArray
        The stabilisation efficiencies for metabolic decay products entering the active pool, decimal proportion.
        Default value: `[0.378]`.
    f_3 : NDArray
        The stabilisation efficiencies for structural decay products entering the slow pool, decimal proportion.
        Default value: `[0.455]`.
    f_5 : NDArray
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal proportion.
        Default value: `[0.0855]`.
    f_6 : NDArray
        The stabilisation efficiencies for slow pool decay products entering the passive pool, decimal proportion.
        Default value: `[0.0504]`.
    f_7 : NDArray
        The stabilisation efficiencies for slow pool decay products entering the active pool, decimal proportion.
        Default value: `[0.42]`.
    f_8 : NDArray
        The stabilisation efficiencies for passive pool decay products entering the active pool, decimal proportion.
        Default value: `[0.45]`.

    Returns
    -------
    NDArray
        The C input to the active soil carbon sub-pool, kg C ha-1.
    """
    beta = _calc_beta(
        carbon_input, lignin_content=lignin_content, nitrogen_content=nitrogen_content
    )

    x = beta * f_1
    y = (carbon_input * (1 - lignin_content) - beta) * f_2
    z = (carbon_input * lignin_content) * f_3 * (f_7 + (f_6 * f_8))
    d = 1 - (f_4 * f_7) - (f_5 * f_8) - (f_4 * f_6 * f_8)
    return (x + y + z) / d


def _calc_beta(
    carbon_input: NDArray,
    lignin_content: NDArray = array(0.073),
    nitrogen_content: NDArray = array(0.0083),
) -> NDArray:
    """
    Equation 5.0G, part 2. Calculate the C input to the metabolic dead organic matter C component, kg C ha-1.

    See table 5.5b for default values for lignin content and nitrogen content.

    Parameters
    ----------
    carbon_input : NDArray
        Total carbon input to the soil, kg C ha-1.
    lignin_content : NDArray
        The average lignin content of carbon input sources, decimal proportion. Default value: `[0.073]`.
    nitrogen_content : NDArray
        The average nitrogen content of carbon sources, decimal proportion. Default value: `[0.0083]`.

    Returns
    -------
    NDArray
        The C input to the metabolic dead organic matter C component, kg C ha-1.
    """
    return carbon_input * (0.85 - 0.018 * (lignin_content / nitrogen_content))


def _calc_active_pool_decay_rate(
    temperature_factor_annual: NDArray,
    water_factor_annual: NDArray,
    tillage_factor: NDArray,
    sand_content: NDArray = array(0.33),
    active_decay_factor: NDArray = array(7.4),
) -> NDArray:
    """
    Equation 5.0B, part 3. Calculate the decay rate for the active SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    temperature_factor_annual : NDArray
        Average annual temperature factor, dimensionless. All elements between `0` and `1`.
    water_factor_annual : NDArray
        Average annual water factor, dimensionless. All elements between `0.31935` and `2.25`.
    tillage_factor : NDArray
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    sand_content : NDArray
        The sand content of the soil, decimal proportion. Default value: `[0.33]`.
    active_decay_factor : NDArray
        decay rate constant under optimal conditions for decomposition of the active SOC subpool, year-1. Default value:
        `[7.4]`.

    Returns
    -------
    NDArray
        The decay rate for active SOC sub-pool, year-1.
    """
    sand_factor = 0.25 + (0.75 * sand_content)
    return (
        temperature_factor_annual
        * water_factor_annual
        * tillage_factor
        * sand_factor
        * active_decay_factor
    )


def _calc_active_pool_steady_state(
    alpha: NDArray, active_pool_decay_rate: NDArray
) -> NDArray:
    """
    Equation 5.0B part 2. Calculate the steady state active sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    alpha : NDArray
        The C input to the active soil carbon sub-pool, kg C ha-1.
    active_pool_decay_rate : NDArray
        Decay rate for active SOC sub-pool, year-1.

    Returns
    -------
    NDArray
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1
    """
    return alpha / active_pool_decay_rate


def _calc_slow_pool_decay_rate(
    temperature_factor_annual: NDArray,
    water_factor_annual: NDArray,
    tillage_factor: NDArray,
    slow_decay_factor: NDArray = array(0.209),
) -> NDArray:
    """
    Equation 5.0C, part 3. Calculate the decay rate for the slow SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    temperature_factor_annual : NDArray
        Average annual temperature factor, dimensionless. All elements between `0` and `1`.
    water_factor_annual : NDArray
        Average annual water factor, dimensionless. All elements between `0.31935` and `2.25`.
    tillage_factor : NDArray
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    slow_decay_factor : NDArray
        The decay rate constant under optimal conditions for decomposition of the slow SOC subpool, year-1.
        Default value: `0.209`.

    Returns
    -------
    NDArray
        The decay rate for slow SOC sub-pool, year-1.
    """
    return (
        temperature_factor_annual
        * water_factor_annual
        * tillage_factor
        * slow_decay_factor
    )


def _calc_slow_pool_steady_state(
    carbon_input: NDArray,
    f_4: NDArray,
    active_pool_steady_state: NDArray,
    active_pool_decay_rate: NDArray,
    slow_pool_decay_rate: NDArray,
    lignin_content: NDArray = array(0.073),
    f_3: NDArray = array(0.455),
) -> NDArray:
    """
    Equation 5.0C, part 2. Calculate the steady state slow sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    carbon_input : NDArray
        Total carbon input to the soil, kg C ha-1.
    f_4 : NDArray
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    active_pool_steady_state : NDArray
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1
    active_pool_decay_rate : NDArray
        Decay rate for active SOC sub-pool, year-1.
    slow_pool_decay_rate : NDArray
        Decay rate for slow SOC sub-pool, year-1.
    lignin_content : NDArray
        The average lignin content of carbon input sources, decimal proportion. Default value: `[0.073]`.
    f_3 : NDArray
        The stabilisation efficiencies for structural decay products entering the slow pool, decimal proportion.
        Default value: `[0.455]`.

    Returns
    -------
    NDArray
        The steady state slow sub-pool SOC stock given conditions in year y, kg C ha-1.
    """
    x = carbon_input * lignin_content * f_3
    y = active_pool_steady_state * active_pool_decay_rate * f_4
    return (x + y) / slow_pool_decay_rate


def _calc_passive_pool_decay_rate(
    temperature_factor_annual: NDArray,
    water_factor_annual: NDArray,
    passive_decay_factor: NDArray = array(0.00689),
) -> NDArray:
    """
    Equation 5.0D, part 3. Calculate the decay rate for the passive SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    temperature_factor_annual : NDArray
        Average annual temperature factor, dimensionless. All elements between `0` and `1`.
    water_factor_annual : NDArray
        Average annual water factor, dimensionless. All elements between `0.31935` and `2.25`.
    passive_decay_factor : NDArray
        decay rate constant under optimal conditions for decomposition of the passive SOC subpool, year-1.
        Default value: `[0.00689]`.

    Returns
    -------
    NDArray
        The decay rate for passive SOC sub-pool, year-1.
    """
    return temperature_factor_annual * water_factor_annual * passive_decay_factor


def _calc_passive_pool_steady_state(
    active_pool_steady_state: NDArray,
    slow_pool_steady_state: NDArray,
    active_pool_decay_rate: NDArray,
    slow_pool_decay_rate: NDArray,
    passive_pool_decay_rate: NDArray,
    f_5: NDArray = array(0.0855),
    f_6: NDArray = array(0.0504),
) -> NDArray:
    """
    Equation 5.0D, part 2. Calculate the steady state passive sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    active_pool_steady_state : NDArray
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1.
    slow_pool_steady_state : NDArray
        The steady state slow sub-pool SOC stock given conditions in year y, kg C ha-1.
    active_pool_decay_rate : NDArray
        Decay rate for active SOC sub-pool, year-1.
    slow_pool_decay_rate : NDArray
        Decay rate for slow SOC sub-pool, year-1.
    passive_pool_decay_rate : NDArray
        Decay rate for passive SOC sub-pool, year-1.
    f_5 : NDArray
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal proportion.
        Default value: `[0.0855]`.
    f_6 : NDArray
        The stabilisation efficiencies for slow pool decay products entering the passive pool, decimal proportion.
        Default value: `[0.0504]`.

    Returns
    -------
    NDArray
        The steady state passive sub-pool SOC stock given conditions in year y, kg C ha-1.
    """
    x = active_pool_steady_state * active_pool_decay_rate * f_5
    y = slow_pool_steady_state * slow_pool_decay_rate * f_6
    return (x + y) / passive_pool_decay_rate


def _calc_sub_pool_soc_stock(
    sub_pool_steady_state: NDArray,
    previous_sub_pool_soc_stock: NDArray,
    sub_pool_decay_rate: NDArray,
    timestep: int = 1,
) -> NDArray:
    """
    Generalised from equations 5.0B, 5.0C and 5.0D, part 1. Calculate the sub-pool SOC stock in year y, kg C ha-1.

    If `sub_pool_decay_rate > 1` then set its value to `1` for this calculation.

    Parameters
    ----------
    sub_pool_steady_state : NDArray
        The steady state sub-pool SOC stock given conditions in year y, kg C ha-1.
    previous_sub_pool_soc_stock : NDArray
        The sub-pool SOC stock in year y-timestep (by default one year ago), kg C ha-1.
    sub_pool_decay_rate : NDArray
        Decay rate for active SOC sub-pool, year-1.
    timestep : int
        The number of years between current and previous inventory year. Default value = `1`.

    Returns
    -------
    NDArray
        The sub-pool SOC stock in year y, kg C ha-1.
    """
    sub_pool_decay_rate = minimum(1, sub_pool_decay_rate)
    return (
        previous_sub_pool_soc_stock
        + (sub_pool_steady_state - previous_sub_pool_soc_stock)
        * timestep
        * sub_pool_decay_rate
    )


# --- COMPILE TIER 2 INVENTORY ---


def _compile_inventory(
    cycles: list[dict], measurement_nodes: list[dict]
) -> tuple[dict, dict]:
    """
    Builds an annual inventory of data and a dictionary of keyword arguments for the tier 2 model.

    TODO: implement long-term average climate data and annual climate data as back ups for monthly data
    TODO: implement randomisation for `irrigationMonthly` if `startDate` and `endDate` are not provided
    """
    grouped_cycles = group_nodes_by_year(cycles, include_spillovers=True)
    grouped_measurements = group_nodes_by_year(measurement_nodes, mode=GroupNodesByYearMode.DATES)

    grouped_climate_data = _get_grouped_climate_measurements(grouped_measurements)
    grouped_irrigated_monthly = _get_grouped_irrigated_monthly(grouped_cycles)
    grouped_sand_content_measurements = _get_grouped_sand_content_measurements(grouped_measurements)
    grouped_carbon_input_data = _get_grouped_carbon_input_data(grouped_cycles)
    grouped_tillage_categories = _get_grouped_tillage_categories(grouped_cycles)
    grouped_is_paddy_rice = _get_grouped_is_paddy_rice(grouped_cycles)

    grouped_data = merge(
        grouped_climate_data,
        grouped_irrigated_monthly,
        grouped_sand_content_measurements,
        grouped_carbon_input_data,
        grouped_tillage_categories,
        grouped_is_paddy_rice
    )

    grouped_should_run = {
        year: {_InventoryKey.SHOULD_RUN: _should_run_inventory(group)}
        for year, group in grouped_data.items()
    }

    inventory = merge(grouped_data, grouped_should_run)

    # Get a back-up value for sand content if no dated ones are available.
    sand_content = get_node_value(find_term_match(
        [m for m in measurement_nodes if m.get("depthUpper") == DEPTH_UPPER and m.get("depthLower") == DEPTH_LOWER],
        _SAND_CONTENT_TERM_ID,
        {}
    )) / 100

    kwargs = {
        "sand_content": sand_content
    }

    return inventory, kwargs


def _check_12_months(inner_dict: dict, keys: set[Any]):
    """
    Checks whether an inner dict has 12 months of data for each of the required inner keys.

    Parameters
    ----------
    inner_dict : dict
        A dictionary representing one year in a timeseries for the Tier 2 model.
    keys : set[Any]
        The required inner keys.

    Returns
    -------
    bool
        Whether or not the inner dict satisfies the conditions.
    """
    return all(
        len(inner_dict.get(key, [])) == 12 for key in keys
    )


def _get_grouped_climate_measurements(grouped_measurements: dict) -> dict:
    return {
        year: {
            _InventoryKey.TEMP_MONTHLY: non_empty_list(flatten(
                node.get("value", []) for node in measurements if node_term_match(node, _TEMPERATURE_MONTHLY_TERM_ID)
            )),
            _InventoryKey.PRECIP_MONTHLY: non_empty_list(flatten(
                node.get("value", []) for node in measurements if node_term_match(node, _PRECIPITATION_MONTHLY_TERM_ID)
            )),
            _InventoryKey.PET_MONTHLY: non_empty_list(flatten(
                node.get("value", []) for node in measurements if node_term_match(node, _PET_MONTHLY_TERM_ID)
            ))
        } for year, measurements in grouped_measurements.items()
    }


def _get_grouped_irrigated_monthly(grouped_cycles: dict) -> dict:
    return {
        year: {
            _InventoryKey.IRRIGATED_MONTHLY: _get_irrigated_monthly(year, cycles)
        } for year, cycles in grouped_cycles.items()
    }


def _get_irrigated_monthly(year: int, cycles: list[dict]) -> list[bool]:
    # Get practice nodes and add "startDate" and "endDate" from cycle if missing.
    irrigation_nodes = non_empty_list(flatten([
        [
            {
                **{key: cycle.get(key) for key in ["startDate", "endDate"] if cycle.get(key)},
                **node
            } for node in cycle.get("practices", [])
        ] for cycle in cycles
    ]))

    grouped_nodes = group_nodes_by_year_and_month(irrigation_nodes)

    # For each month (1 - 12) check if irrigation is present.
    return [check_irrigation(grouped_nodes.get(year, {}).get(month, [])) for month in range(1, 13)]


def _get_grouped_sand_content_measurements(grouped_measurements: dict) -> dict:
    grouped_sand_content_measurements = {
        year: find_term_match(
            [m for m in measurements if m.get("depthUpper") == DEPTH_UPPER and m.get("depthLower") == DEPTH_LOWER],
            _SAND_CONTENT_TERM_ID,
            {}
        ) for year, measurements in grouped_measurements.items()
    }

    return {
        year: {_InventoryKey.SAND_CONTENT: get_node_value(measurement)/100}
        for year, measurement in grouped_sand_content_measurements.items() if measurement
    }


def _get_grouped_carbon_input_data(grouped_cycles: dict) -> dict:
    grouped_carbon_sources = {
        year: flatten([_get_carbon_sources(cycle) for cycle in cycles])
        for year, cycles in grouped_cycles.items()
    }

    return {
        year: {
            _InventoryKey.CARBON_INPUT: _calc_total_organic_carbon_input(carbon_sources),
            _InventoryKey.N_CONTENT: _calc_average_nitrogen_content_of_organic_carbon_sources(carbon_sources),
            _InventoryKey.LIGNIN_CONTENT: _calc_average_lignin_content_of_organic_carbon_sources(carbon_sources)
        } for year, carbon_sources in grouped_carbon_sources.items()
    }


def _get_carbon_sources(cycle: dict) -> list[CarbonSource]:
    """
    Extract and format the carbon source data from a cycle's inputs and products.

    Carbon sources can be either a HESTIA `Product` node (e.g. crop residue) or `Input` node (e.g. organic amendment).

    Parameters
    ----------
    cycle : list[dict]
        A HESTIA `Cycle` node, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
    list[CarbonSource]
        A formatted list of `CarbonSource`s.
    """
    carbon_source_nodes = filter_list_term_type(
        cycle.get("inputs", []) + cycle.get("practices", []) + cycle.get("products", []),
        _INPUT_CARBON_SOURCE_TERM_TYPES + _PRACTICE_CARBON_SOURCE_TERM_TYPES + _PRODUCT_CARBON_SOURCE_TERM_TYPES
    )

    group_fac = cycle.get('fraction_of_group_duration')
    node_fac = cycle.get('fraction_of_node_duration')

    scaling_fac = group_fac if round(group_fac * 100) >= round(node_fac * 100) else 1

    kwargs = {
        "cycle": cycle,
        "scaling_factor": scaling_fac
    }

    return non_empty_list([
        next(
            (
                _func(node, **kwargs) for validator, _func in _CARBON_SOURCE_DECISION_TREE.items()
                if validator(node)
            ),
            None
        ) for node in carbon_source_nodes
    ])


def _should_run_carbon_source_ag_residue(node: dict) -> bool:
    """
    Determine whether an input or product is a valid above-ground biomass carbon source.

    Parameters
    ----------
    node : dict
        A HESTIA [Input](https://www.hestia.earth/schema/Input) or [Product](https://www.hestia.earth/schema/Product)
        node.

    Returns
    -------
    bool
        Whether the node satisfies the critera.
    """
    return node.get("term", {}).get("@id") == _ABOVE_GROUND_CROP_RESIDUE_TOTAL_TERM_ID


def _calc_carbon_source_ag_crop_residue(
    node: dict, *, cycle: dict, scaling_factor: float, **_
) -> Union[CarbonSource, None]:
    """
    Extract and format the carbon source data for above-ground crop residues.

    n.b., We assume that even if a cycle's residue management states that 100% of above-ground crop residues are
    removed or burnt, a minimal amount of crop residues do remain on site to become a carbon source (see
    `_MIN_RESIDUE_LEFT_ON_FIELD` variable).

    Parameters
    ----------
    node : dict
        A HESTIA [Product](https://www.hestia.earth/schema/Product) node with `term.termType` == `landCover`.
    cycle : dict
        The HESTIA [Cycle](https://www.hestia.earth/schema/Cycle) that produces the crop residue.
    scaling_factor : float
        The scaling factor for the mass of carbon input, calculated by estimating how much the cycle overlaps
        with the current inventory year.

    Returns
    -------
    CarbonSource | None
        The carbon source data of the above-ground residues, or `None` if carbon source data incomplete.
    """
    value = get_node_value(node)
    residue_left_on_field = list_sum([
        get_node_value(practice) for practice in cycle.get("practices", [])
        if node_term_match(practice, _CROP_RESIDUE_MANAGEMENT_TERM_IDS)
    ])
    mass = value * max(residue_left_on_field, _MIN_RESIDUE_LEFT_ON_FIELD) * scaling_factor / 100

    carbon_content, nitrogen_content, lignin_content, dry_matter = _retrieve_carbon_source_properties(node)

    carbon_source = CarbonSource(
        mass * dry_matter if dry_matter else mass,
        carbon_content / dry_matter if dry_matter else carbon_content,
        nitrogen_content / dry_matter if dry_matter else nitrogen_content,
        lignin_content / dry_matter if dry_matter else lignin_content
    )

    return carbon_source if _validate_carbon_source(carbon_source) else None


def _should_run_carbon_source_cover_crop(node: dict) -> bool:
    """
    Determine whether a product is a valid cover crop carbon source.

    Parameters
    ----------
    node : dict
        A HESTIA [Input](https://www.hestia.earth/schema/Input) or [Product](https://www.hestia.earth/schema/Product)
        node.

    Returns
    -------
    bool
        Whether the node satisfies the critera.
    """
    LOOKUP = LOOKUPS["landCover"]
    TARGET_LOOKUP_VALUES = IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE[IpccLandUseCategory.ANNUAL_CROPS]

    return (
        node.get("term", {}).get("termType") in [TermTermType.LANDCOVER.value]
        and is_cover_crop(node)
        and node_lookup_match(node, LOOKUP, TARGET_LOOKUP_VALUES)
    )


def _calc_carbon_source_cover_crop(node: dict, *, scaling_factor: float, **_) -> Union[CarbonSource, None]:
    """
    Extract and format the carbon source data for an annual cover crop.

    n.b., We make the assumption that the entirety of the cover crop's biomass remains on site.

    Parameters
    ----------
    node : dict
        A HESTIA [Product](https://www.hestia.earth/schema/Product) node with `term.termType` == `landCover`.
    scaling_factor : float
        The scaling factor for the mass of carbon input, calculated by estimating how much the cycle overlaps
        with the current inventory year.

    Returns
    -------
    CarbonSource | None
        The carbon source data of the cover crop, or `None` if carbon source data incomplete.
    """
    value = get_node_value(node)
    carbon_source = CarbonSource(
        _DEFAULT_COVER_CROP_BIOMASS * value * scaling_factor / 100,
        _Parameter.DEFAULT_CARBON_CONTENT.value.get("value"),
        _Parameter.DEFAULT_NITROGEN_CONTENT.value.get("value"),
        _Parameter.DEFAULT_NITROGEN_CONTENT.value.get("value")
    )
    return carbon_source


def _should_run_carbon_source(node: dict) -> bool:
    """
    Determine whether an input or product is a valid carbon source.

    Parameters
    ----------
    node : dict
        A HESTIA [Input](https://www.hestia.earth/schema/Input) or [Product](https://www.hestia.earth/schema/Product)
        node.

    Returns
    -------
    bool
        Whether the node satisfies the critera.
    """
    return any([
        node.get("term", {}).get("@id") in _CARBON_SOURCE_TERM_IDS,
        node.get("term", {}).get("termType") in _INPUT_CARBON_SOURCE_TERM_TYPES
    ])


def _calc_carbon_source(node: dict, *, scaling_factor: float, **_) -> Union[CarbonSource, None]:
    """
    Extract and format the carbon source data for an input or product.

    Parameters
    ----------
    node : dict
        A HESTIA [Input](https://www.hestia.earth/schema/Input) or [Product](https://www.hestia.earth/schema/Product)
        node.
    scaling_factor : float
        The scaling factor for the mass of carbon input, calculated by estimating how much the cycle overlaps
        with the current inventory year.


    Returns
    -------
    CarbonSource | None
        The carbon source data of the cover crop, or `None` if carbon source data incomplete.
    """
    mass = get_node_value(node) * scaling_factor
    carbon_content, nitrogen_content, lignin_content, dry_matter = _retrieve_carbon_source_properties(node)

    carbon_source = CarbonSource(
        mass * dry_matter if dry_matter else mass,
        carbon_content / dry_matter if dry_matter else carbon_content,
        nitrogen_content / dry_matter if dry_matter else nitrogen_content,
        lignin_content / dry_matter if dry_matter else lignin_content
    )

    return carbon_source if _validate_carbon_source(carbon_source) else None


def _retrieve_carbon_source_properties(node: dict) -> tuple[float, float, float, float]:
    """
    Extract the carbon source properties from an input or product node or, if required, retrieve them from default
    properties.

    Parameters
    ----------
    node : dict
        A HESTIA [Input](https://www.hestia.earth/schema/Input) or [Product](https://www.hestia.earth/schema/Product)
        node.

    Returns
    -------
    tuple[float, float, float]
        `(carbon_content, nitrogen_content, lignin_content, dry_matter)`
    """
    return (
        get_node_property(node, term_id).get("value", 0)/100 for term_id in _CARBON_INPUT_PROPERTY_TERM_IDS
    )


def _validate_carbon_source(carbon_source: CarbonSource) -> bool:
    """
    Validate that a `CarbonSource` named tuple is data complete.
    """
    return all([
        carbon_source.mass > 0,
        0 < carbon_source.carbon_content <= 1,
        0 < carbon_source.nitrogen_content <= 1,
        0 < carbon_source.lignin_content <= 1
    ])


_CARBON_SOURCE_DECISION_TREE = {
    _should_run_carbon_source_ag_residue: _calc_carbon_source_ag_crop_residue,
    _should_run_carbon_source_cover_crop: _calc_carbon_source_cover_crop,
    _should_run_carbon_source: _calc_carbon_source,
}


def _calc_total_organic_carbon_input(
    carbon_sources: list[CarbonSource], default_carbon_content=0.42
) -> float:
    """
    Equation 5.0H part 1. Calculate the total organic carbon to a site from all carbon sources (above-ground and
    below-ground crop residues, organic amendments, etc.).

    Parameters
    ----------
    carbon_sources : list[CarbonSource])
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`.
    default_carbon_content : float
        The default carbon content of a carbon source, decimal proportion, kg C (kg d.m.)-1.

    Returns
    -------
    float
        The total mass of organic carbon inputted into the site, kg C ha-1.
    """
    return sum(c.mass * (c.carbon_content if c.carbon_content else default_carbon_content) for c in carbon_sources)


def _calc_average_nitrogen_content_of_organic_carbon_sources(
    carbon_sources: list[CarbonSource], default_nitrogen_content=0.0085
) -> float:
    """
    Calculate the average nitrogen content of the carbon inputs through a weighted mean.

    Parameters
    ----------
    carbon_sources : list[CarbonSource]
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`.
    default_nitrogen_content : float
        The default nitrogen content of a carbon source, decimal proportion, kg N (kg d.m.)-1.

    Returns
    -------
    float
        The average nitrogen content of the carbon sources, decimal_proportion, kg N (kg d.m.)-1.
    """
    total_weight = sum(c.mass for c in carbon_sources)
    weighted_values = [
        c.mass * (c.nitrogen_content if c.nitrogen_content else default_nitrogen_content) for c in carbon_sources
    ]
    should_run_ = total_weight > 0
    return sum(weighted_values) / total_weight if should_run_ else 0


def _calc_average_lignin_content_of_organic_carbon_sources(
    carbon_sources: list[CarbonSource], default_lignin_content=0.073
) -> float:
    """
    Calculate the average lignin content of the carbon inputs through a weighted mean.

    Parameters
    ----------
    carbon_sources : list[CarbonSource]
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`.
    default_lignin_content : float
        The default lignin content of a carbon source, decimal proportion, kg lignin (kg d.m.)-1.

    Returns
    -------
    float
        The average lignin content of the carbon sources, decimal_proportion, kg lignin (kg d.m.)-1.
    """
    total_weight = sum(c.mass for c in carbon_sources)
    weighted_values = [
        c.mass * (c.lignin_content if c.lignin_content else default_lignin_content) for c in carbon_sources
    ]
    should_run_ = total_weight > 0
    return sum(weighted_values) / total_weight if should_run_ else 0


def _get_grouped_tillage_categories(grouped_cycles):
    return {
        year: {
            _InventoryKey.TILLAGE_CATEGORY: _assign_tier_2_ipcc_tillage_management_category(cycles)
        } for year, cycles in grouped_cycles.items()
    }


def _assign_tier_2_ipcc_tillage_management_category(
    cycles: list[dict],
    default: IpccManagementCategory = IpccManagementCategory.UNKNOWN
) -> IpccManagementCategory:
    """
    Assigns a tillage `IpccManagementCategory` to a list of HESTIA `Cycle`s.

    Parameters
    ----------
    cycles : list[dict])
        A list of HESTIA `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
        IpccManagementCategory: The assigned tillage `IpccManagementCategory`.
    """
    return next(
        (
            key for key in _TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE
            if _TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE[key](cycles, key)
        ),
        default
    ) if len(cycles) > 0 else default


_TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.FULL_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    ),
    IpccManagementCategory.REDUCED_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    ),
    IpccManagementCategory.NO_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    )
}


def _check_cycle_tillage_management_category(
    cycle: dict,
    key: IpccManagementCategory
) -> bool:
    """
    Checks whether a Hesita `Cycle` node meets the requirements of a specific tillage `IpccManagementCategory`.

    Parameters
    ----------
    cycle : dict
        A HESTIA `Cycle` node, see: https://www.hestia.earth/schema/Cycle.
    key : IpccManagementCategory
        The `IpccManagementCategory` to match.

    Returns
    -------
    bool
        Whether or not the cycle meets the requirements for the category.
    """
    LOOKUP = LOOKUPS["tillage"]
    target_lookup_values = IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE.get(key, None)

    practices = cycle.get("practices", [])
    tillage_nodes = filter_list_term_type(
        practices, [TermTermType.TILLAGE]
    )

    return cumulative_nodes_lookup_match(
        tillage_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    ) and (
        key is not IpccManagementCategory.NO_TILLAGE
        or _check_zero_tillages(tillage_nodes)
    )


def _check_zero_tillages(practices: list[dict]) -> bool:
    """
    Checks whether a list of `Practice`s nodes describe 0 total tillages, or not.

    Parameters
    ----------
    practices : list[dict]
        A list of HESTIA `Practice` nodes, see: https://www.hestia.earth/schema/Practice.

    Returns
    -------
    bool
        Whether or not 0 tillages counted.
    """
    practice = find_term_match(practices, _NUMBER_OF_TILLAGES_TERM_ID)
    nTillages = list_sum(practice.get("value", []))
    return nTillages <= 0


def _get_grouped_is_paddy_rice(grouped_cycles: dict) -> dict:
    return {
        year: {
            _InventoryKey.IS_PADDY_RICE: _check_is_paddy_rice(cycles)
        } for year, cycles in grouped_cycles.items()
    }


def _check_is_paddy_rice(cycles: list[dict]) -> bool:
    LOOKUP = LOOKUPS["crop"]
    TARGET_LOOKUP_VALUES = IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE.get(
        IpccLandUseCategory.PADDY_RICE_CULTIVATION, None
    )

    has_paddy_rice_products = any(cumulative_nodes_lookup_match(
        filter_list_term_type(
            cycle.get("products", []) + cycle.get("practices", []),
            [TermTermType.CROP, TermTermType.FORAGE, TermTermType.LANDCOVER]
        ),
        lookup=LOOKUP,
        target_lookup_values=TARGET_LOOKUP_VALUES,
        cumulative_threshold=MIN_YIELD_THRESHOLD,
        default_node_value=MIN_YIELD_THRESHOLD
    ) for cycle in cycles)

    has_upland_rice_products = any(cumulative_nodes_term_match(
        filter_list_term_type(
            cycle.get("products", []) + cycle.get("practices", []),
            [TermTermType.CROP, TermTermType.FORAGE, TermTermType.LANDCOVER]
        ),
        target_term_ids=get_upland_rice_crop_terms() + get_upland_rice_land_cover_terms(),
        cumulative_threshold=MIN_YIELD_THRESHOLD,
        default_node_value=MIN_YIELD_THRESHOLD
    ) for cycle in cycles)

    has_irrigation = any(
        check_irrigation(filter_list_term_type(cycle.get("practices", []), [TermTermType.WATERREGIME]))
        for cycle in cycles
    )

    return has_paddy_rice_products or (has_upland_rice_products and has_irrigation)


def _should_run_inventory(group: dict) -> bool:
    """
    Determines whether there is sufficient data in an inventory year to run the tier 2 model.

    1. Check that the cycle is not for paddy rice.
    2. Check if monthly data has a value for each calendar month.
    3. Check if all required keys are present.

    Parameters
    ----------
    group : dict
        Dictionary containing information for a specific inventory year.

    Returns
    -------
    bool
        True if the inventory year is valid, False otherwise.
    """
    monthly_data_complete = _check_12_months(
        group,
        {
            _InventoryKey.TEMP_MONTHLY,
            _InventoryKey.PRECIP_MONTHLY,
            _InventoryKey.PET_MONTHLY,
            _InventoryKey.IRRIGATED_MONTHLY
        }
    )

    carbon_input_data_complete = all([
        group.get(_InventoryKey.CARBON_INPUT, 0) > 0,
        group.get(_InventoryKey.N_CONTENT, 0) > 0,
        group.get(_InventoryKey.LIGNIN_CONTENT, 0) > 0,
    ])

    return all([
        not group.get(_InventoryKey.IS_PADDY_RICE),
        monthly_data_complete,
        carbon_input_data_complete,
        all(key in group.keys() for key in _REQUIRED_KEYS),
    ])
