from enum import Enum
from functools import lru_cache, reduce
from itertools import product
import numpy as np
import numpy.typing as npt
from typing import Any, Callable, Literal, Optional, TypedDict, Union
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, SiteSiteType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float
from hestia_earth.utils.stats import gen_seed, repeat_single, truncated_normal_1d
from hestia_earth.utils.descriptive_stats import calc_descriptive_stats

from hestia_earth.models.log import debugMissingLookup, log_as_table, logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import group_nodes_by_year
from hestia_earth.models.utils.ecoClimateZone import EcoClimateZone, get_eco_climate_zone_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.lookup import get_region_lookup_value
from hestia_earth.models.utils.site import related_cycles

from . import MODEL
from .biomass_utils import BiomassCategory, get_valid_management_nodes, summarise_land_cover_nodes

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "management": [
                {
                    "@type": "Management",
                    "value": "",
                    "term.termType": "landCover",
                    "endDate": "",
                    "optional": {
                        "startDate": ""
                    }
                }
            ],
            "measurements": [
                {
                    "@type": "Measurement",
                    "value": "",
                    "term.@id": "ecoClimateZone",
                    "none": {
                        "value": ["5, 6"]
                    }
                }
            ],
            "none": {
                "siteType": ["glass or high accessible cover"]
            }
        }
    }
}
LOOKUPS = {
    "emissionToAirNaturalVegetationBurning_emissionCategory_gEmittedPerKgDryMatterCombusted": [
        "IPCC_2019_G_EMITTED_PER_KG_DRY_MATTER_COMBUSTED_{EMISSION_CATEGORY}_value",
        "IPCC_2019_G_EMITTED_PER_KG_DRY_MATTER_COMBUSTED_{EMISSION_CATEGORY}_sd"
    ],
    "ipcc2019FuelCategory_tonnesDryMatterCombustedPerHaBurned": "value",
    "landCover": "BIOMASS_CATEGORY",
    "region-percentageAreaBurnedDuringForestClearance": "percentage_area_burned_during_forest_clearance"
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "statsDefinition": "simulated",
        "observations": "",
        "dates": "",
        "methodClassification": "tier 1 model"
    }]
}
TERM_ID = 'ch4ToAirNaturalVegetationBurning,coToAirNaturalVegetationBurning,n2OToAirNaturalVegetationBurningDirect,noxToAirNaturalVegetationBurning'  # noqa: E501

EMISSION_TERM_IDS = TERM_ID.split(",")
TIER = EmissionMethodTier.TIER_1.value
STATS_DEFINITION = EmissionStatsDefinition.SIMULATED.value

_ITERATIONS = 10000  # N interations for which the model will run as a Monte Carlo simulation
_AMORTISATION_PERIOD = 20  # Emissions should be amortised over 20 years

_EXCLUDED_ECO_CLIMATE_ZONES = {EcoClimateZone.POLAR_MOIST, EcoClimateZone.POLAR_DRY}
_EXCLUDED_SITE_TYPES = {SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value}
_NATURAL_VEGETATION_CATEGORIES = {
    BiomassCategory.FOREST,
    BiomassCategory.NATURAL_FOREST,
    BiomassCategory.PLANTATION_FOREST
}
_DEFAULT_FACTOR = {"value": 0}
_DEFAULT_PERCENT_BURNED = 0


class _FuelCategory(Enum):
    """
    Natural vegetation fuel categories from IPCC (2019).
    """
    BOREAL_FOREST = "boreal-forest"
    EUCALYPT_FOREST = "eucalypt-forest"
    NATURAL_TROPICAL_FOREST = "natural-tropical-forest"  # mean of primary and secondary tropical forest
    PRIMARY_TROPICAL_FOREST = "primary-tropical-forest"
    SAVANNA_GRASSLAND_EARLY_DRY_SEASON_BURNS = "savanna-grassland-early-dry-season-burns"
    SAVANNA_GRASSLAND_MID_TO_LATE_DRY_SEASON_BURNS = "savanna-grassland-mid-to-late-dry-season-burns"
    SAVANNA_WOODLAND_EARLY_DRY_SEASON_BURNS = "savanna-woodland-early-dry-season-burns"
    SAVANNA_WOODLAND_MID_TO_LATE_DRY_SEASON_BURNS = "savanna-woodland-mid-to-late-dry-season-burns"
    SECONDARY_TROPICAL_FOREST = "secondary-tropical-forest"
    SHRUBLAND = "shrubland"
    TEMPERATE_FOREST = "temperate-forest"
    TERTIARY_TROPICAL_FOREST = "tertiary-tropical-forest"
    UNKNOWN_TROPICAL_FOREST = "unknown-tropical-forest"  # mean of primary, secondary and tertiary tropical forest


class _EmissionCategory(Enum):
    """
    Natural vegetation burning emission categories from IPCC (2019).
    """
    AGRICULTURAL_RESIDUES = "agricultural-residues"
    BIOFUEL_BURNING = "biofuel-burning"
    OTHER_FOREST = "other-forest"
    SAVANNA_AND_GRASSLAND = "savanna-and-grassland"
    TROPICAL_FOREST = "tropical-forest"


_EmissionTermId = Literal[
    "ch4ToAirNaturalVegetationBurning",
    "coToAirNaturalVegetationBurning",
    "n2OToAirNaturalVegetationBurningDirect",
    "noxToAirNaturalVegetationBurning"
]


class _InventoryYear(TypedDict, total=False):
    biomass_category_summary: dict[BiomassCategory, float]
    natural_vegetation_delta: dict[BiomassCategory, float]
    fuel_burnt_per_category: dict[_FuelCategory, npt.NDArray]
    annual_emissions: dict[_EmissionTermId, npt.NDArray]
    amortised_emissions: dict[_EmissionTermId, npt.NDArray]
    share_of_emissions: dict[str, float]  # {cycle_id (str): value, ...}
    allocated_emissions: dict[_EmissionTermId, dict[str, npt.NDArray]]


_InventoryKey = Literal[
    "biomass_category_summary",
    "natural_vegetation_delta",
    "fuel_burnt_per_category",
    "annual_emissions",
    "amortised_emissions",
    "share_of_emissions",
    "allocated_emissions"
]

_Inventory = dict[int, _InventoryYear]
"""
{year (int): data (_InventoryYear)}
"""


_BIOMASS_CATEGORY_TO_FUEL_CATEGORY = {
    BiomassCategory.FOREST: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.WARM_TEMPERATE_DRY: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.COOL_TEMPERATE_MOIST: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.COOL_TEMPERATE_DRY: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.BOREAL_MOIST: _FuelCategory.BOREAL_FOREST,
        EcoClimateZone.BOREAL_DRY: _FuelCategory.BOREAL_FOREST,
        EcoClimateZone.TROPICAL_MONTANE: _FuelCategory.UNKNOWN_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_WET: _FuelCategory.UNKNOWN_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_MOIST: _FuelCategory.UNKNOWN_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_DRY: _FuelCategory.UNKNOWN_TROPICAL_FOREST
    },
    BiomassCategory.NATURAL_FOREST: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.WARM_TEMPERATE_DRY: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.COOL_TEMPERATE_MOIST: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.COOL_TEMPERATE_DRY: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.BOREAL_MOIST: _FuelCategory.BOREAL_FOREST,
        EcoClimateZone.BOREAL_DRY: _FuelCategory.BOREAL_FOREST,
        EcoClimateZone.TROPICAL_MONTANE: _FuelCategory.NATURAL_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_WET: _FuelCategory.NATURAL_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_MOIST: _FuelCategory.NATURAL_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_DRY: _FuelCategory.NATURAL_TROPICAL_FOREST
    },
    BiomassCategory.PLANTATION_FOREST: {
        EcoClimateZone.WARM_TEMPERATE_MOIST: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.WARM_TEMPERATE_DRY: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.COOL_TEMPERATE_MOIST: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.COOL_TEMPERATE_DRY: _FuelCategory.TEMPERATE_FOREST,
        EcoClimateZone.BOREAL_MOIST: _FuelCategory.BOREAL_FOREST,
        EcoClimateZone.BOREAL_DRY: _FuelCategory.BOREAL_FOREST,
        EcoClimateZone.TROPICAL_MONTANE: _FuelCategory.TERTIARY_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_WET: _FuelCategory.TERTIARY_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_MOIST: _FuelCategory.TERTIARY_TROPICAL_FOREST,
        EcoClimateZone.TROPICAL_DRY: _FuelCategory.TERTIARY_TROPICAL_FOREST
    }
}
"""
Mapping from IPCC biomass category and eco-climate zone to natural vegetation fuel category.
"""

_FUEL_CATEGORY_TO_EMISSION_CATEGORY = {
    _FuelCategory.BOREAL_FOREST: _EmissionCategory.OTHER_FOREST,
    _FuelCategory.EUCALYPT_FOREST: _EmissionCategory.OTHER_FOREST,
    _FuelCategory.NATURAL_TROPICAL_FOREST: _EmissionCategory.TROPICAL_FOREST,
    _FuelCategory.PRIMARY_TROPICAL_FOREST: _EmissionCategory.TROPICAL_FOREST,
    _FuelCategory.SAVANNA_GRASSLAND_EARLY_DRY_SEASON_BURNS: _EmissionCategory.SAVANNA_AND_GRASSLAND,
    _FuelCategory.SAVANNA_GRASSLAND_MID_TO_LATE_DRY_SEASON_BURNS: _EmissionCategory.SAVANNA_AND_GRASSLAND,
    _FuelCategory.SAVANNA_WOODLAND_EARLY_DRY_SEASON_BURNS: _EmissionCategory.SAVANNA_AND_GRASSLAND,
    _FuelCategory.SAVANNA_WOODLAND_MID_TO_LATE_DRY_SEASON_BURNS: _EmissionCategory.SAVANNA_AND_GRASSLAND,
    _FuelCategory.SECONDARY_TROPICAL_FOREST: _EmissionCategory.TROPICAL_FOREST,
    _FuelCategory.SHRUBLAND: _EmissionCategory.SAVANNA_AND_GRASSLAND,
    _FuelCategory.TEMPERATE_FOREST: _EmissionCategory.OTHER_FOREST,
    _FuelCategory.TERTIARY_TROPICAL_FOREST: _EmissionCategory.TROPICAL_FOREST,
    _FuelCategory.UNKNOWN_TROPICAL_FOREST: _EmissionCategory.TROPICAL_FOREST
}
"""
Mapping from natural vegetation fuel category to natural vegetation burning emission category.
"""


def _get_fuel_category(biomass_category: BiomassCategory, eco_climate_zone: EcoClimateZone) -> _FuelCategory:
    """
    Get the IPCC (2019) natural vegetation fuel category that corresponds to a specific combination of biomass category
    and eco-climate zone.
    """
    return _BIOMASS_CATEGORY_TO_FUEL_CATEGORY.get(biomass_category, {}).get(eco_climate_zone)


def _get_emission_category(fuel_category: _FuelCategory) -> _EmissionCategory:
    """
    Get the IPCC (2019) emission category that corresponds to a fuel category.
    """
    return _FUEL_CATEGORY_TO_EMISSION_CATEGORY.get(fuel_category)


def _sample_truncated_normal(
    *, iterations: int, value: float, sd: float, seed: Union[int, np.random.Generator, None] = None, **_
) -> npt.NDArray:
    """
    Randomly sample a model parameter with a truncated normal distribution. Neither fuel factors nor emission factors
    can be below 0, so truncated normal sampling used.
    """
    return truncated_normal_1d(shape=(1, iterations), mu=value, sigma=sd, low=0, high=np.inf, seed=seed)


def _sample_constant(*, iterations: int, value: float, **_) -> npt.NDArray:
    """Sample a constant model parameter."""
    return repeat_single(shape=(1, iterations), value=value)


_KWARGS_TO_SAMPLE_FUNC = {
    # ("value", "se", "n"): _sample_standard_error_normal,
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


def _get_fuel_factor(fuel_category: _FuelCategory) -> dict:
    """
    Retrieve distribution data for a specific fuel category.
    """
    LOOKUP_KEY = "ipcc2019FuelCategory_tonnesDryMatterCombustedPerHaBurned"
    LOOKUP_FILENAME = f"{LOOKUP_KEY}.csv"
    TARGET_DATA = (
        "value",
        # "se",  # useless without n data
        # "n"  # TODO: add n data to lookup
    )

    row = fuel_category.name

    lookup = download_lookup(LOOKUP_FILENAME)

    data = {
        target: get_table_value(lookup, column_name("FuelCategory"), row, column_name(target))
        for target in TARGET_DATA
    }

    for term_id, target in product(EMISSION_TERM_IDS, TARGET_DATA):
        debugMissingLookup(LOOKUP_FILENAME, "FuelCategory", row, target, data.get(target), model=MODEL, term=term_id)

    return (
        {
            k: parsed for k, v in data.items() if (parsed := safe_parse_float(v, default=None)) is not None
        }  # remove missing
        or _DEFAULT_FACTOR  # if parsed dict empty, return default
    )


def _get_emission_factor(term_id: _EmissionTermId, emission_category: _EmissionCategory) -> dict:
    """
    Retrieve distribution data for a specific emission and emission category.
    """
    LOOKUP_KEY = "emissionToAirNaturalVegetationBurning_emissionCategory_gEmittedPerKgDryMatterCombusted"
    LOOKUP_FILENAME = f"{LOOKUP_KEY}.csv"
    TARGET_DATA = ("value", "sd")

    row = term_id
    column_root = f"IPCC_2019_G_EMITTED_PER_KG_DRY_MATTER_COMBUSTED_{emission_category.name}"

    lookup = download_lookup(LOOKUP_FILENAME)

    data = {
        target: get_table_value(lookup, column_name("term.id"), row, column_name(f"{column_root}_{target}"))
        for target in TARGET_DATA
    }

    for target in TARGET_DATA:
        debugMissingLookup(
            LOOKUP_FILENAME, "term.id", row, f"{column_root}_{target}", data.get(target), model=MODEL, term=term_id
        )

    return (
        {
            k: parsed for k, v in data.items() if (parsed := safe_parse_float(v, default=None)) is not None
        }  # remove missing
        or _DEFAULT_FACTOR  # if parsed dict empty, return default
    )


def _sample_fuel_factor(
    fuel_category: _FuelCategory, *, seed: Union[int, np.random.Generator, None] = None
) -> npt.NDArray:
    """
    Generate random samples from a fuel factor's distribution data.
    """
    factor_data = _get_fuel_factor(fuel_category)
    sample_func = _get_sample_func(factor_data)
    return sample_func(iterations=_ITERATIONS, seed=seed, **factor_data)


def _sample_emission_factor(
    term_id: _EmissionTermId,
    emission_category: _EmissionCategory,
    *,
    seed: Union[int, np.random.Generator, None] = None
) -> npt.NDArray:
    """
    Generate random samples from an emission factor's distribution data.
    """
    factor_data = _get_emission_factor(term_id, emission_category)
    sample_func = _get_sample_func(factor_data)
    return sample_func(iterations=_ITERATIONS, seed=seed, **factor_data)


def _emission(term_id: str, **kwargs) -> dict:
    """
    Build a HESTIA [Emission node](https://www.hestia.earth/schema/Emission) using model output data.
    """
    emission = _new_emission(term_id, MODEL)
    return emission | {
        **{k: v for k, v in kwargs.items()},
        "methodTier": TIER
    }


def _get_site(cycle: dict) -> dict:
    """
    Get the site data from a [Cycle node](https://www.hestia.earth/schema/Cycle).

    Used as a test utility to mock the 'site' data in during testing.
    """
    return cycle.get("site", {})


def get_percent_burned(site: str):
    LOOKUP_KEY = "region-percentageAreaBurnedDuringForestClearance"
    LOOKUP_FILENAME = f"{LOOKUP_KEY}.csv"
    country_id = site.get("country", {}).get("@id")

    value = get_region_lookup_value(LOOKUP_FILENAME, country_id, LOOKUPS[LOOKUP_KEY])
    return safe_parse_float(value, _DEFAULT_PERCENT_BURNED)


def _calc_burnt_fuel(area_converted: npt.NDArray, fuel_factor: npt.NDArray, frac_burnt: npt.NDArray) -> npt.NDArray:
    """
    Calculate the amount of fuel burnt during a fire event.

    Parameters
    ----------
    area_converted : NDArray
        Area of land converted (ha).
    fuel_factor : NDArray
        Conversion factor (kg fuel per ha of land cover converted).
    frac_burnt : NDArray
        The fraction of land converted using burning during a land use change event (decimal percentage, 0-1).

    Returns
    -------
    NDArray
        The mass of burnt fuel (kg)
    """
    return area_converted * fuel_factor * frac_burnt


def _build_fuel_burnt_accumulator(
    percent_burned: npt.ArrayLike,
    eco_climate_zone: EcoClimateZone,
    sample_fuel_factor_func: Callable[[_FuelCategory], npt.NDArray]
):
    """
    Build an `accumulate_fuel_burnt` function to reduce natural vegetation deltas into mass of fuel burnt per
    `_FuelCategory`.

    Parameters
    ----------
    percent_burned : NDArray
        The percentage of land converted using burning during a land use change event (percentage, 0-100%).
    eco_climate_zone : EcoClimateZone
        The eco-climate zone of the Site.
    sample_fuel_factor_func : Callable[[_FuelCategory], npt.NDArray]
        Function to sample fuel factor parameter.

    Returns
    -------
    NDArray
        The mass of burnt fuel (kg)
    """
    frac_burnt = percent_burned / 100

    def accumulate_fuel_burnt(
        result: dict[_FuelCategory, npt.NDArray], biomass_category: BiomassCategory, delta: float
    ) -> dict[_FuelCategory, npt.NDArray]:
        """
        Calculate the amount of fuel burnt when natural vegetation is lost. Accumulate fuel burnt by `_FuelCategory`.

        Parameters
        ----------
        result : dict[_FuelCategory, npt.NDArray]
            A dict with the format `{_FuelCategory: kg_fuel_burnt (npt.NDArray)}`.
        biomass_category : BiomassCategory
            A biomass category undergoing change during a LUC event.
        delta : float
            The change in land cover for the biomass category (% area).

        Returns
        -------
        dict[_FuelCategory, npt.NDArray]
        """

        fuel_category = _get_fuel_category(biomass_category, eco_climate_zone)
        fuel_factor = sample_fuel_factor_func(fuel_category)

        area_converted = abs(delta) / 100 if delta < 0 else 0  # We only care about losses

        already_burnt = result.get(fuel_category, np.array(0))

        update_dict = {} if area_converted == 0 else {
            fuel_category: already_burnt + _calc_burnt_fuel(area_converted, fuel_factor, frac_burnt)
        }

        return result | update_dict

    return accumulate_fuel_burnt


def _calc_emission(fuel_burnt: npt.NDArray, emission_factor: npt.NDArray,) -> npt.NDArray:
    """
    Calculate the emission from a fuel burning.

    Parameters
    ----------
    fuel_burnt : NDArray
        The mass of burnt fuel (kg).
    emission_factor : NDArray
        Conversion factor (kg emission per kg of fuel burnt).

    Returns
    -------
    NDArray
        The mass of emission (kg)
    """
    return fuel_burnt * emission_factor


def _sum_cycle_emissions(term_id: _EmissionTermId, cycle_id: str, inventory: _Inventory) -> npt.NDArray:
    """
    Sum the emissions allocated to a cycle.
    """
    KEY = "allocated_emissions"

    def add_cycle_emissions(result: npt.NDArray, year: int) -> npt.NDArray:
        allocated_emissions = inventory.get(year, {}).get(KEY, {}).get(term_id, {})
        return result + allocated_emissions.get(cycle_id, np.array(0))

    return reduce(add_cycle_emissions, inventory.keys(), np.array(0))


def _compile_inventory(
    cycle: dict, site: dict, land_cover_nodes: list[dict], eco_climate_zone: EcoClimateZone
):
    """
    Compile the run data for the model, collating data from `site.management` and related cycles. An annualised
    inventory of land cover change and natural vegetation burning events is constructed. Emissions from burning events
    are estimated, amortised over 20 years and allocated to cycles.

    Parameters
    ----------
    cycle : dict
        The HESTIA [Cycle](https://www.hestia.earth/schema/Cycle) the model is running on.
    site : dict
        The HESTIA [Site](https://www.hestia.earth/schema/Site) the Cycle takes place on.
    land_cover_nodes : list[dict]
        Valid land cover [Management nodes](https://www.hestia.earth/schema/Management) extracted from the Site.
    eco_climate_zone : EcoClimateZone
        The eco-climate zone of the Site.

    Returns
    -------
    should_run : bool
        Whether the model should be run.
    inventory : _Inventory
        An inventory of model data.
    logs : dict
        Data about the inventory compilation to be logged.
    """
    cycle_id = cycle.get("@id")
    related_cycles_ = related_cycles(site, cycles_mapping={cycle_id: cycle})

    seed = gen_seed(site, MODEL, TERM_ID)
    rng = np.random.default_rng(seed)

    cycles_grouped = group_nodes_by_year(related_cycles_)
    land_cover_grouped = group_nodes_by_year(land_cover_nodes)
    percent_burned = get_percent_burned(site)

    @lru_cache(maxsize=len(_FuelCategory))
    def sample_fuel_factor(*args):
        """Fuel factors should not be re-sampled between years, so cache results."""
        return _sample_fuel_factor(*args, seed=rng)

    @lru_cache(maxsize=len(EMISSION_TERM_IDS)*len(_EmissionCategory))
    def sample_emission_factor(*args):
        """Emission factors should not be re-sampled between years, so cache results."""
        return _sample_emission_factor(*args, seed=rng)

    accumulate_fuel_burnt = _build_fuel_burnt_accumulator(percent_burned, eco_climate_zone, sample_fuel_factor)

    def build_inventory_year(inventory: _Inventory, year: int) -> dict:
        """
        Parameters
        ----------
        inventory : _Inventory
            An inventory of model data.
        year : int
            The year of the inventory to build.

        Returns
        -------
        inventory : dict
            An inventory of model data, updated to include the input year.
        """
        land_cover_nodes = land_cover_grouped.get(
            next(
                (k for k in sorted(land_cover_grouped) if k >= year),  # backfill if possible
                min(land_cover_grouped, key=lambda k: abs(k - year))   # else forward-fill
            ),
            []
        )

        biomass_category_summary = summarise_land_cover_nodes(land_cover_nodes)
        prev_biomass_category_summary = inventory.get(year-1, {}).get("biomass_category_summary", {})

        natural_vegetation_delta = {
            category: biomass_category_summary.get(category, 0) - prev_biomass_category_summary.get(category, 0)
            for category in _NATURAL_VEGETATION_CATEGORIES
        }

        fuel_burnt_per_category = reduce(
            lambda result, item: accumulate_fuel_burnt(result, *item),
            natural_vegetation_delta.items(),
            dict()
        )

        annual_emissions = {
            term_id: sum(
                _calc_emission(amount, sample_emission_factor(term_id, _get_emission_category(fuel_category)))
                for fuel_category, amount in fuel_burnt_per_category.items()
            ) for term_id in EMISSION_TERM_IDS
        }

        previous_years = list(inventory.keys())
        amortisation_slice_index = max(0, len(previous_years) - (_AMORTISATION_PERIOD - 1))
        amortisation_years = previous_years[amortisation_slice_index:]  # get the previous 19 years, if available

        amortised_emissions = {
            term_id: 0.05 * (
                annual_emissions[term_id] + sum(
                    inventory[year_]["annual_emissions"][term_id] for year_ in amortisation_years
                )
            ) for term_id in EMISSION_TERM_IDS
        }

        cycles = cycles_grouped.get(year, [])
        total_cycle_duration = sum(c.get("fraction_of_group_duration", 0) for c in cycles)

        share_of_emissions = {
            cycle["@id"]: cycle.get("fraction_of_group_duration", 0) / total_cycle_duration
            for cycle in cycles
        }

        allocated_emissions = {
            term_id: {
                cycle_id: share_of_emission * amortised_emissions[term_id]
                for cycle_id, share_of_emission in share_of_emissions.items()
            }
            for term_id in EMISSION_TERM_IDS
        }

        inventory[year] = _InventoryYear(
            biomass_category_summary=biomass_category_summary,
            natural_vegetation_delta=natural_vegetation_delta,
            fuel_burnt_per_category=fuel_burnt_per_category,
            annual_emissions=annual_emissions,
            amortised_emissions=amortised_emissions,
            share_of_emissions=share_of_emissions,
            allocated_emissions=allocated_emissions
        )

        return inventory

    all_years = list(cycles_grouped.keys()) + list(land_cover_grouped.keys())
    min_year, max_year = min(all_years), max(all_years)

    inventory = reduce(build_inventory_year, range(min_year, max_year+1), dict())

    n_land_cover_years = len(land_cover_grouped)

    logs = {
        "n_land_cover_years": n_land_cover_years,
        "percent_burned": percent_burned,
        "seed": seed,
    }

    should_run = bool(inventory and n_land_cover_years > 1)

    return should_run, inventory, logs


def _format_bool(value: Optional[bool]) -> str:
    """Format a bool for logging in a table."""
    return str(bool(value))


def _format_number(value: Optional[float], unit: Optional[str] = None) -> str:
    """Format a float for logging in a table."""
    return f"{value:.1f}{f' {unit}' if unit else ''}" if isinstance(value, (float, int)) else "None"


def _format_nd_array(value: Optional[npt.NDArray], unit: Optional[str] = None) -> str:
    """Format a numpy array for logging in a table."""
    return (
        f"{_format_number(value.mean())} ± {_format_number(value.std())}" + f"{f' {unit}' if unit else ''}"
        if isinstance(value, np.ndarray) else "None"
    )


def _format_decimal_percentage(value: Optional[float], unit: Optional[str] = "pct") -> str:
    """Format a decimal percentage (0-1) as a percentage (0-100%) for logging in a table."""
    return _format_number(value * 100, unit) if isinstance(value, (float, int)) else "None"


_INVALID_CHARS = {"_", ":", ",", "="}
_REPLACEMENT_CHAR = "-"


def _format_str(value: str, *_) -> str:
    """Format a string for logging in a table. Remove all characters used to render the table on the front end."""
    return reduce(lambda x, char: x.replace(char, _REPLACEMENT_CHAR), _INVALID_CHARS, str(value))


def _format_column_header(*keys: tuple[Union[Enum, str], ...]) -> str:
    """Format a variable number of enums and strings for logging as a table column header."""
    return " ".join(_format_str(k.value if isinstance(k, Enum) else str(k)) for k in keys)


def _format_eco_climate_zone(value: EcoClimateZone) -> str:
    """Format an eco-climate zone for logging."""
    return (
        _format_str(str(value.name).lower().replace("_", " ").capitalize()) if isinstance(value, EcoClimateZone)
        else "None"
    )


_LOGS_FORMAT_DATA: dict[str, Callable] = {
    "has_valid_site_type": _format_bool,
    "eco_climate_zone": _format_eco_climate_zone,
    "has_valid_eco_climate_zone": _format_bool,
    "has_land_cover_nodes": _format_bool,
    "should_compile_inventory": _format_bool,
    "percent_burned": lambda x: _format_number(x, "pct"),
}
_DEFAULT_FORMAT_FUNC = _format_str


def _format_logs(logs: dict) -> dict[str, str]:
    """
    Format model logs - excluding the inventory data, which must be formatted separately.
    """
    return {key: _LOGS_FORMAT_DATA.get(key, _DEFAULT_FORMAT_FUNC)(value) for key, value in logs.items()}


_INVENTORY_FORMAT_DATA: dict[_InventoryKey, dict[Literal["filter_by", "format_func"], Any]] = {
    "fuel_burnt_per_category": {
        "format_func": lambda x: _format_nd_array(x, "kg")
    },
    "annual_emissions": {
        "filter_by": ("term_id", ),
        "format_func": lambda x: _format_nd_array(x, "kg")
    },
    "amortised_emissions": {
        "filter_by": ("term_id", ),
        "format_func": lambda x: _format_nd_array(x, "kg")
    },
    "share_of_emissions": {
        "filter_by": ("cycle_id", ),
        "format_func": _format_decimal_percentage
    },
    "allocated_emissions": {
        "filter_by": ("term_id", "cycle_id"),
        "format_func": lambda x: _format_nd_array(x, "kg")
    }
}
"""
Mapping between inventory key and formatting options for logging in a table. Inventory keys not included in the dict
will not be logged in the table.
"""


def _flatten_dict(d: dict) -> dict[tuple, Any]:
    """
    Flatten a nested dict, returns dict with keys as tuples with format `(key_level_1, key_level_2, ..., key_level_n)`.
    """
    def flatten(d: dict, c: Optional[list] = None):
        c = c or []
        for a, b in d.items():
            if not isinstance(b, dict):
                yield (tuple(c+[a]), b)
            else:
                yield from flatten(b, c+[a])

    return dict(flatten(d))


def _get_relevant_inner_keys(
    term_id: _EmissionTermId,
    cycle_id: str,
    key: str,
    inventory: _Inventory,
    *,
    filter_by: Optional[tuple[Literal["term_id", "cycle_id"], ...]] = None,
    **_
) -> list[tuple]:
    """
    Get the column headings for the formatted table. Nested inventory values should be flattened, with nested keys
    being transformed into a tuple with the format `(key_level_1, key_level_2, ..., key_level_n)`.

    Inner keys not relevant to the emission term being logged or the cycle the model is running on should be excluded.
    """
    FILTER_VALUES = {"term_id": term_id, "cycle_id": cycle_id}
    filter_target = (
        tuple(val for f in filter_by if (val := FILTER_VALUES.get(f)))
        if filter_by else None
    )

    inner_keys = {
        tuple(k) for inner in inventory.values() for k in _flatten_dict(inner.get(key, {}))
        if not filter_target or k == filter_target
    }

    return sorted(
        inner_keys,
        key=lambda category: category.value if isinstance(category, Enum) else str(category)
    )


def _format_inventory(term_id: _EmissionTermId, cycle_id: str, inventory: dict) -> str:
    """
    Format the inventory for logging as a table.

    Extract relevant data, flatten nested dicts and format inventory values based on expected data type.
    """
    relevant_inventory_keys = {
        inventory_key: _get_relevant_inner_keys(term_id, cycle_id, inventory_key, inventory, **kwargs)
        for inventory_key, kwargs in _INVENTORY_FORMAT_DATA.items()
    }

    return log_as_table(
        {
            "year": year,
            **{
                _format_column_header(inventory_key, *inner_key): _INVENTORY_FORMAT_DATA[inventory_key]["format_func"](
                    reduce(lambda d, k: d.get(k, {}), [year, inventory_key, *inner_key], inventory)
                )
                for inventory_key, relevant_inner_keys in relevant_inventory_keys.items()
                for inner_key in relevant_inner_keys
            }
        } for year in inventory
    ) if inventory else "None"


def _log_emission_data(should_run: bool, term_id: _EmissionTermId, cycle: dict, inventory: dict, logs: dict):
    """
    Format and log the model logs and inventory.
    """
    formatted_logs = _format_logs(logs)
    formatted_inventory = _format_inventory(term_id, cycle.get("@id"), inventory)

    logRequirements(cycle, model=MODEL, term=term_id, **formatted_logs, inventory=formatted_inventory)
    logShouldRun(cycle, MODEL, term_id, should_run)


def _should_run(cycle: dict):
    """
    Extract, organise and pre-process required data from the input [Cycle node](https://www.hestia.earth/schema/Site)
    and determine whether the model should run.

    Parameters
    ----------
    cycle : dict
        A HESTIA [Cycle](https://www.hestia.earth/schema/Cycle).

    Returns
    -------
    tuple[bool, _Inventory]
        should_run, inventory
    """
    site = _get_site(cycle)

    site_type = site.get("siteType")
    eco_climate_zone = get_eco_climate_zone_value(site, as_enum=True)

    land_cover_nodes = get_valid_management_nodes(site)

    has_valid_site_type = all([site_type, site_type not in _EXCLUDED_SITE_TYPES])
    has_valid_eco_climate_zone = all([eco_climate_zone, eco_climate_zone not in _EXCLUDED_ECO_CLIMATE_ZONES])
    has_land_cover_nodes = len(land_cover_nodes) > 1

    should_compile_inventory = all([
        has_valid_site_type,
        has_valid_eco_climate_zone,
        has_land_cover_nodes
    ])

    should_run, inventory, compilation_logs = (
        _compile_inventory(cycle, site, land_cover_nodes, eco_climate_zone)
        if should_compile_inventory else (False, {}, {})
    )

    logs = {
        "site_id": site.get("@id"),
        "site_type": site_type,
        "has_valid_site_type": has_valid_site_type,
        "eco_climate_zone": eco_climate_zone,
        "has_valid_eco_climate_zone": has_valid_eco_climate_zone,
        "has_land_cover_nodes": has_land_cover_nodes,
        "should_compile_inventory": should_compile_inventory,
        **compilation_logs
    }

    for term_id in EMISSION_TERM_IDS:
        _log_emission_data(should_run, term_id, cycle, inventory, logs)

    return should_run, inventory


def _run_emission(term_id: _EmissionTermId, cycle_id: str, inventory: _Inventory) -> list[dict]:
    """
    Retrieve the sum relevant emissions and format them as a HESTIA
    [Emission node](https://www.hestia.earth/schema/Emission).
    """
    emission = _sum_cycle_emissions(term_id, cycle_id, inventory)
    descriptive_stats = calc_descriptive_stats(emission, STATS_DEFINITION, decimals=3)
    return _emission(term_id, **descriptive_stats)


def run(cycle: dict):
    """
    Run the `nonCo2EmissionsToAirNaturalVegetationBurning` model on a Cycle.

    Parameters
    ----------
    cycle : dict
        A HESTIA [Cycle](https://www.hestia.earth/schema/Cycle).

    Returns
    -------
    list[dict]
        A list of HESTIA [Emission](https://www.hestia.earth/schema/Emission) nodes with `term.termType` =
        `ch4ToAirNaturalVegetationBurning` **OR** `coToAirNaturalVegetationBurning` **OR**
        `n2OToAirNaturalVegetationBurningDirect` **OR** `noxToAirNaturalVegetationBurning`.
    """
    should_run, inventory = _should_run(cycle)
    return [_run_emission(term_id, cycle.get("@id"), inventory) for term_id in EMISSION_TERM_IDS] if should_run else []
