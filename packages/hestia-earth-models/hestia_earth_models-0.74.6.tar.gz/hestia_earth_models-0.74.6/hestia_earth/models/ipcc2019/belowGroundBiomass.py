from enum import Enum
from functools import reduce
from numpy import average, copy, random, vstack
from numpy.typing import NDArray
from typing import Optional, Union
from hestia_earth.schema import (
    MeasurementMethodClassification,
    MeasurementStatsDefinition,
    SiteSiteType
)
from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.stats import gen_seed
from hestia_earth.utils.descriptive_stats import calc_descriptive_stats

from hestia_earth.models.log import log_as_table, logRequirements, logShouldRun
from hestia_earth.models.utils import pairwise
from hestia_earth.models.utils.blank_node import group_nodes_by_year
from hestia_earth.models.utils.ecoClimateZone import EcoClimateZone, get_eco_climate_zone_value
from hestia_earth.models.utils.source import get_source
from hestia_earth.models.utils.measurement import _new_measurement

from . import MODEL
from .biomass_utils import (
    BiomassCategory, get_valid_management_nodes, detect_land_cover_change, group_by_biomass_category,
    sample_biomass_equilibrium, summarise_land_cover_nodes
)


REQUIREMENTS = {
    "Site": {
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
                "value": ["1", "2", "3", "4", "7", "8", "9", "10", "11", "12"],
                "term.@id": "ecoClimateZone"
            }
        ],
        "none": {
            "siteType": ["glass or high accessible cover"]
        }
    }
}
LOOKUPS = {
    "landCover": "BIOMASS_CATEGORY",
    "ecoClimateZone": [
        "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_FOREST",
        "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_NATURAL_FOREST",
        "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_PLANTATION_FOREST",
        "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_OTHER"
    ]
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
        "methodClassification": "tier 1 model"
    }]
}
TERM_ID = 'belowGroundBiomass'
BIBLIO_TITLE = '2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories'
OTHER_BIBLIO_TITLES = [
    '2006 IPCC Guidelines for National Greenhouse Gas Inventories',
    'COMMISSION DECISION of 10 June 2010 on guidelines for the calculation of land carbon stocks for the purpose of Annex V to Directive 2009/28/EC'  # noqa: E501
]

_ITERATIONS = 10000
_DEPTH_UPPER = 0
_DEPTH_LOWER = 30
_METHOD_CLASSIFICATION = MeasurementMethodClassification.TIER_1_MODEL.value
_STATS_DEFINITION = MeasurementStatsDefinition.SIMULATED.value

_EQUILIBRIUM_TRANSITION_PERIOD = 20
_EXCLUDED_ECO_CLIMATE_ZONES = {EcoClimateZone.POLAR_MOIST, EcoClimateZone.POLAR_DRY}
_EXCLUDED_SITE_TYPES = {
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
}

_VALID_BIOMASS_CATEGORIES = {
    BiomassCategory.FOREST,
    BiomassCategory.NATURAL_FOREST,
    BiomassCategory.PLANTATION_FOREST
}
"""Biomass stock data is only available in the lookups for these categories."""


class _InventoryKey(Enum):
    """
    The inner keys of the annualised inventory created by the `_compile_inventory` function.

    The value of each enum member is formatted to be used as a column header in the `log_as_table` function.
    """
    BIOMASS_CATEGORY_SUMMARY = "biomass-categories"
    LAND_COVER_CHANGE_EVENT = "lcc-event"
    YEARS_SINCE_LCC_EVENT = "years-since-lcc-event"
    REGIME_START_YEAR = "regime-start-year"


_REQUIRED_INVENTORY_KEYS = [e for e in _InventoryKey]


def run(site: dict) -> list[dict]:
    """
    Run the model on a Site.

    Parameters
    ----------
    site : dict
        A valid HESTIA [Site](https://www.hestia.earth/schema/Site).

    Returns
    -------
    list[dict]
        A list of HESTIA [Measurement](https://www.hestia.earth/schema/Measurement) nodes with `term.termType` =
        `aboveGroundBiomass`
    """
    should_run, inventory, kwargs = _should_run(site)
    return _run(site, inventory, iterations=_ITERATIONS, **kwargs) if should_run else []


def _should_run(site: dict) -> tuple[bool, dict, dict]:
    """
    Extract and re-organise required data from the input [Site](https://www.hestia.earth/schema/Site) node and determine
    whether the model should run.

    Parameters
    ----------
    site : dict
        A valid HESTIA [Site](https://www.hestia.earth/schema/Site).

    Returns
    -------
    tuple[bool, dict, dict]
        should_run, inventory, kwargs
    """
    site_type = site.get("siteType")
    eco_climate_zone = get_eco_climate_zone_value(site, as_enum=True)

    land_cover = get_valid_management_nodes(site)

    has_valid_site_type = site_type not in _EXCLUDED_SITE_TYPES
    has_valid_eco_climate_zone = all([
        eco_climate_zone,
        eco_climate_zone not in _EXCLUDED_ECO_CLIMATE_ZONES
    ])
    has_land_cover_nodes = len(land_cover) > 0

    should_compile_inventory = all([
        has_valid_site_type,
        has_valid_eco_climate_zone,
        has_land_cover_nodes
    ])

    inventory = _compile_inventory(land_cover) if should_compile_inventory else {}
    kwargs = {
        "eco_climate_zone": eco_climate_zone,
        "seed": gen_seed(site, MODEL, TERM_ID)
    }

    logRequirements(
        site, model=MODEL, term=TERM_ID,
        site_type=site_type,
        has_valid_site_type=has_valid_site_type,
        has_valid_eco_climate_zone=has_valid_eco_climate_zone,
        has_land_cover_nodes=has_land_cover_nodes,
        **kwargs,
        inventory=_format_inventory(inventory)
    )

    should_run = all([
        len(inventory) > 0,
        all(data for data in inventory.values() if all(key in data.keys() for key in _REQUIRED_INVENTORY_KEYS))
    ])

    logShouldRun(site, MODEL, TERM_ID, should_run)

    return should_run, inventory, kwargs


def _compile_inventory(land_cover_nodes: list[dict]) -> dict:
    """
    Build an annual inventory of model input data.

    Returns a dict with shape:
    ```
    {
        year (int): {
            _InventoryKey.BIOMASS_CATEGORY_SUMMARY: {
                category (BiomassCategory): value (float),
                ...categories
            },
            _InventoryKey.LAND_COVER_CHANGE_EVENT: value (bool),
            _InventoryKey.YEARS_SINCE_LCC_EVENT: value (int),
            _InventoryKey.REGIME_START_YEAR: value (int)
        },
        ...years
    }
    ```

    Parameters
    ----------
    land_cover_nodes : list[dict]
        A list of HESTIA [Management](https://www.hestia.earth/schema/Measurement) nodes with `term.termType` =
        `landCover`

    Returns
    -------
    dict
        The inventory of data.
    """
    land_cover_grouped = group_nodes_by_year(land_cover_nodes)
    min_year, max_year = min(land_cover_grouped.keys()), max(land_cover_grouped.keys())

    def build_inventory_year(inventory: dict, year_pair: tuple[int, int]) -> dict:
        """
        Build a year of the inventory using the data from `land_cover_categories_grouped`.

        Parameters
        ----------
        inventory: dict
            The land cover change portion of the inventory. Must have the same shape as the returned dict.
        year_pair : tuple[int, int]
            A tuple with the shape `(prev_year, current_year)`.

        Returns
        -------
        dict
            The land cover change portion of the inventory.
        """

        prev_year, current_year = year_pair
        land_cover_nodes = land_cover_grouped.get(current_year, {})

        biomass_category_summary = summarise_land_cover_nodes(land_cover_nodes, group_by_biomass_category)

        prev_biomass_category_summary = inventory.get(prev_year, {}).get(_InventoryKey.BIOMASS_CATEGORY_SUMMARY, {})
        is_lcc_event = detect_land_cover_change(biomass_category_summary, prev_biomass_category_summary)

        time_delta = current_year - prev_year
        prev_years_since_lcc_event = inventory.get(prev_year, {}).get(_InventoryKey.YEARS_SINCE_LCC_EVENT, 0)
        years_since_lcc_event = time_delta if is_lcc_event else prev_years_since_lcc_event + time_delta
        regime_start_year = current_year - years_since_lcc_event

        equilibrium_year = regime_start_year + _EQUILIBRIUM_TRANSITION_PERIOD
        inventory_years = set(list(inventory.keys()) + list(land_cover_grouped.keys()))

        should_add_equilibrium_year = (
            min_year < equilibrium_year < max_year       # Is the year relevant?
            and equilibrium_year not in inventory_years  # Is the year missing?
            and equilibrium_year < current_year          # Is it the first inventory year after the equilibrium?
        )

        current_data = {
            _InventoryKey.BIOMASS_CATEGORY_SUMMARY: biomass_category_summary,
            _InventoryKey.LAND_COVER_CHANGE_EVENT: is_lcc_event,
            _InventoryKey.YEARS_SINCE_LCC_EVENT: years_since_lcc_event,
            _InventoryKey.REGIME_START_YEAR: regime_start_year
        }

        equilibrium_data = {
            **current_data,
            _InventoryKey.YEARS_SINCE_LCC_EVENT: _EQUILIBRIUM_TRANSITION_PERIOD
        }

        update_dict = {
            current_year: current_data,
            **({equilibrium_year: equilibrium_data} if should_add_equilibrium_year else {})
        }

        return inventory | update_dict

    start_year = list(land_cover_grouped)[0]
    initial_land_cover_nodes = land_cover_grouped.get(start_year, {})

    initial = {
        start_year: {
            _InventoryKey.BIOMASS_CATEGORY_SUMMARY: summarise_land_cover_nodes(
                initial_land_cover_nodes, group_by_biomass_category
            ),
            _InventoryKey.LAND_COVER_CHANGE_EVENT: False,
            _InventoryKey.YEARS_SINCE_LCC_EVENT: _EQUILIBRIUM_TRANSITION_PERIOD,
            _InventoryKey.REGIME_START_YEAR: start_year - _EQUILIBRIUM_TRANSITION_PERIOD
        }
    }

    return dict(sorted(
        reduce(
            build_inventory_year,
            pairwise(land_cover_grouped.keys()),  # Inventory years need data from previous year to be compiled.
            initial
        ).items()
    ))


def _format_inventory(inventory: dict) -> str:
    """
    Format the SOC inventory for logging as a table. Rows represent inventory years, columns represent soc stock change
    data for each measurement method classification present in inventory. If the inventory is invalid, return `"None"`
    as a string.
    """
    inventory_years = sorted(set(non_empty_list(years for years in inventory.keys())))
    land_covers = _get_unique_categories(inventory, _InventoryKey.BIOMASS_CATEGORY_SUMMARY)
    inventory_keys = _get_loggable_inventory_keys(inventory)

    should_run = inventory and len(inventory_years) > 0

    return log_as_table(
        {
            "year": year,
            **{
                _format_column_header(category): _format_number(
                    inventory.get(year, {}).get(_InventoryKey.BIOMASS_CATEGORY_SUMMARY, {}).get(category, 0)
                ) for category in land_covers
            },
            **{
                _format_column_header(key): _INVENTORY_KEY_TO_FORMAT_FUNC[key](
                    inventory.get(year, {}).get(key)
                ) for key in inventory_keys
            }
        } for year in inventory_years
    ) if should_run else "None"


def _get_unique_categories(inventory: dict, key: _InventoryKey) -> list:
    """
    Extract the unique biomass or land cover categories from the inventory.

    Can be used to cache sampled parameters for each `BiomassCategory` or to log land covers.
    """
    categories = reduce(
        lambda result, categories: result | set(categories),
        (inner.get(key, {}).keys() for inner in inventory.values()),
        set()
    )
    return sorted(
        categories,
        key=lambda category: category.value if isinstance(category, Enum) else str(category),
    )


def _get_loggable_inventory_keys(inventory: dict) -> list:
    """
    Return a list of unique inventory keys in a fixed order.
    """
    unique_keys = reduce(
        lambda result, keys: result | set(keys),
        (
            (key for key in group.keys() if key in _INVENTORY_KEY_TO_FORMAT_FUNC)
            for group in inventory.values()
        ),
        set()
    )
    key_order = {key: i for i, key in enumerate(_INVENTORY_KEY_TO_FORMAT_FUNC.keys())}
    return sorted(unique_keys, key=lambda key_: key_order[key_])


def _format_bool(value: Optional[bool]) -> str:
    """Format a bool for logging in a table."""
    return str(bool(value))


def _format_number(value: Optional[float]) -> str:
    """Format a float for logging in a table."""
    return f"{value:.1f}" if isinstance(value, (float, int)) else "None"


def _format_column_header(value: Union[_InventoryKey, BiomassCategory, str]):
    """Format an enum or str for logging as a table column header."""
    as_string = value.value if isinstance(value, Enum) else str(value)
    return as_string.replace(" ", "-")


_INVENTORY_KEY_TO_FORMAT_FUNC = {
    _InventoryKey.LAND_COVER_CHANGE_EVENT: _format_bool,
    _InventoryKey.YEARS_SINCE_LCC_EVENT: _format_number
}
"""
Map inventory keys to format functions. The columns in inventory logged as a table will also be sorted in the order of
the `dict` keys.
"""


def _run(
    site: dict,
    inventory: dict,
    *,
    eco_climate_zone: EcoClimateZone,
    iterations: int,
    seed: Union[int, random.Generator, None] = None
) -> list[dict]:
    """
    Calculate the annual above ground biomass stock based on an inventory of land cover data.

    Inventory should be a dict with shape:
    ```
    {
        year (int): {
            _InventoryKey.BIOMASS_CATEGORY_SUMMARY: {
                category (BiomassCategory): value (float),
                ...categories
            },
            _InventoryKey.LAND_COVER_CHANGE_EVENT: value (bool),
            _InventoryKey.YEARS_SINCE_LCC_EVENT: value (int),
            _InventoryKey.REGIME_START_YEAR: value (int)
        },
        ...years
    }
    ```

    Parameters
    ----------
    inventory : dict
        The annual inventory of land cover data.
    ecoClimateZone : EcoClimateZone
        The eco-climate zone of the site.
    iterations: int
        The number of iterations to run the model as a Monte Carlo simulation.
    seed : int | random.Generator | None
        The seed for the random sampling of model parameters.

    Returns
    -------
    list[dict]
        A list of HESTIA [Measurement](https://www.hestia.earth/schema/Measurement) nodes with `term.termType` =
        `aboveGroundBiomass`
    """
    rng = random.default_rng(seed)
    unique_biomass_categories = _get_unique_categories(inventory, _InventoryKey.BIOMASS_CATEGORY_SUMMARY)

    timestamps = list(inventory.keys())

    factor_cache = {
        category: sample_biomass_equilibrium(iterations, category, eco_climate_zone, _build_col_name, seed=rng)
        for category in unique_biomass_categories
    }

    def get_average_equilibrium(year) -> NDArray:
        biomass_categories = inventory.get(year, {}).get(_InventoryKey.BIOMASS_CATEGORY_SUMMARY, {})
        values = [factor_cache.get(category) for category in biomass_categories.keys()]
        weights = [weight for weight in biomass_categories.values()]
        return average(values, axis=0, weights=weights)

    equilibrium_annual = vstack([get_average_equilibrium(year) for year in inventory.keys()])

    def calc_biomass_stock(result: NDArray, index_year: tuple[int, int]) -> NDArray:
        index, year = index_year

        years_since_llc_event = inventory.get(year, {}).get(_InventoryKey.YEARS_SINCE_LCC_EVENT, 0)
        regime_start_year = inventory.get(year, {}).get(_InventoryKey.REGIME_START_YEAR, 0)
        regime_start_index = (
            timestamps.index(regime_start_year) if regime_start_year in timestamps else 0
        )

        regime_start_biomass = result[regime_start_index]
        current_biomass_equilibrium = equilibrium_annual[index]

        time_ratio = min(years_since_llc_event / _EQUILIBRIUM_TRANSITION_PERIOD, 1)
        biomass_delta = (current_biomass_equilibrium - regime_start_biomass) * time_ratio

        result[index] = regime_start_biomass + biomass_delta
        return result

    biomass_annual = reduce(
        calc_biomass_stock,
        list(enumerate(timestamps))[1:],
        copy(equilibrium_annual)
    )

    descriptive_stats = calc_descriptive_stats(
        biomass_annual,
        _STATS_DEFINITION,
        axis=1,     # Calculate stats rowwise.
        decimals=6  # Round values to the nearest milligram.
    )
    return [_measurement(timestamps, **descriptive_stats) | get_source(site, BIBLIO_TITLE, OTHER_BIBLIO_TITLES)]


def _build_col_name(biomass_category: BiomassCategory) -> str:
    """
    Get the column name for the `ecoClimateZone-lookup.csv` for a specific biomass category equilibrium.
    """
    COL_NAME_ROOT = "BG_BIOMASS_EQUILIBRIUM_KG_C_HECTARE_"
    return (
        f"{COL_NAME_ROOT}{biomass_category.name}" if biomass_category in _VALID_BIOMASS_CATEGORIES
        else f"{COL_NAME_ROOT}OTHER"
    )


def _measurement(
    timestamps: list[int],
    value: list[float],
    *,
    sd: list[float] = None,
    min: list[float] = None,
    max: list[float] = None,
    statsDefinition: str = None,
    observations: list[int] = None
) -> dict:
    """
    Build a Hestia `Measurement` node to contain a value and descriptive statistics calculated by the models.

    Parameters
    ----------
    timestamps : list[int]
        A list of calendar years associated to the calculated SOC stocks.
    value : list[float]
        A list of values representing the mean biomass stock for each year of the inventory
    sd : list[float]
        A list of standard deviations representing the standard deviation of the biomass stock for each year of the
        inventory.
    min : list[float]
        A list of minimum values representing the minimum modelled biomass stock for each year of the inventory.
    max : list[float]
        A list of maximum values representing the maximum modelled biomass stock for each year of the inventory.
    statsDefinition : str
        The [statsDefinition](https://hestia.earth/schema/Measurement#statsDefinition) of the measurement.
    observations : list[int]
        The number of model iterations used to calculate the descriptive statistics.

    Returns
    -------
    dict
        A valid HESTIA `Measurement` node, see: https://www.hestia.earth/schema/Measurement.
    """
    update_dict = {
        "value": value,
        "sd": sd,
        "min": min,
        "max": max,
        "statsDefinition": statsDefinition,
        "observations": observations,
        "dates": [f"{year}-12-31" for year in timestamps],
        "methodClassification": _METHOD_CLASSIFICATION
    }
    measurement = _new_measurement(TERM_ID, MODEL) | {
        key: value for key, value in update_dict.items() if value
    }
    measurement["depthUpper"] = _DEPTH_UPPER
    measurement["depthLower"] = _DEPTH_LOWER
    return measurement
