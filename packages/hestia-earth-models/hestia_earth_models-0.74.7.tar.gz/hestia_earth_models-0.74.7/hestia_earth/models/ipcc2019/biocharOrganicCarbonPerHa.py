from functools import reduce
import numpy as np
from typing import Union

from hestia_earth.schema import (
    CycleFunctionalUnit, MeasurementMethodClassification, MeasurementStatsDefinition, SiteSiteType, TermTermType
)

from hestia_earth.utils.blank_node import get_node_value
from hestia_earth.utils.descriptive_stats import calc_descriptive_stats
from hestia_earth.utils.stats import gen_seed, truncated_normal_1d
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import log_as_table, logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import group_nodes_by_year, filter_list_term_type
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.site import related_cycles
from hestia_earth.models.utils.term import get_lookup_value

from .organicCarbonPerHa_utils import IpccSoilCategory
from .organicCarbonPerHa_tier_1 import _assign_ipcc_soil_category

from . import MODEL


REQUIREMENTS = {
    "Site": {
        "siteType": ["cropland", "permanent pasture"],
        "related": {
            "Cycle": [{
                "endDate": "",
                "functionalUnit": "1 ha",
                "optional": {
                    "startDate": "",
                    "inputs": [{
                        "@type": "Input",
                        "term.termType": "biochar"
                    }]
                }
            }]
        }
    }
}
LOOKUPS = {
    "biochar": [
        "FRAC_OC_REMAINING_100_YEARS",
        "FRAC_OC_REMAINING_100_YEARS_SD"
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
        "depthUpper": "",
        "depthLower": "",
        "methodClassification": "tier 1 model"
    }]
}
TERM_ID = 'biocharOrganicCarbonPerHa'

_ITERATIONS = 1000
_DEPTH_UPPER = 0
_DEPTH_LOWER = 30
_METHOD_CLASSIFICATION = MeasurementMethodClassification.TIER_1_MODEL.value
_STATS_DEFINITION = MeasurementStatsDefinition.SIMULATED.value

_VALID_SITE_TYPES = [SiteSiteType.CROPLAND.value, SiteSiteType.PERMANENT_PASTURE.value]
_VALID_FUNCTIONAL_UNITS = [CycleFunctionalUnit._1_HA.value]


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
    should_run, inventory = _should_run(site)
    return _run(inventory) if should_run else []


def _should_run(site: dict) -> tuple[bool, dict]:
    """
    Extract and organise required data from the input [Site](https://www.hestia.earth/schema/Site) node and determine
    whether the model should run.

    Parameters
    ----------
    site : dict
        A valid HESTIA [Site](https://www.hestia.earth/schema/Site).

    Returns
    -------
    tuple[bool, dict, dict]
        should_run, inventory
    """
    cycles = related_cycles(site)
    site_type = site.get("siteType")
    ipcc_soil_category = _assign_ipcc_soil_category(site.get("measurements", []))

    has_cycles = len(cycles) > 0
    has_valid_site_type = site_type in _VALID_SITE_TYPES
    has_functional_unit_1_ha = all(cycle.get("functionalUnit") in _VALID_FUNCTIONAL_UNITS for cycle in cycles)
    has_mineral_soils = ipcc_soil_category not in [IpccSoilCategory.ORGANIC_SOILS]

    seed = gen_seed(site, MODEL, TERM_ID)
    rng = np.random.default_rng(seed)

    should_compile_inventory = all([
        has_cycles,
        has_valid_site_type,
        has_functional_unit_1_ha,
        has_mineral_soils
    ])

    inventory, logs = _compile_inventory(cycles, rng) if should_compile_inventory else ({}, {})

    logRequirements(
        site, model=MODEL, term=TERM_ID,
        has_cycles=has_cycles,
        site_type=site_type,
        has_valid_site_type=has_valid_site_type,
        has_functional_unit_1_ha=has_functional_unit_1_ha,
        has_mineral_soils=has_mineral_soils,
        ipcc_soil_category=ipcc_soil_category,
        should_compile_inventory=should_compile_inventory,
        seed=seed,
        inventory=_format_inventory(inventory),
        **_format_logs(logs)
    )

    should_run = all([
        len(inventory) > 0  # are there any cycles?
    ])

    logShouldRun(site, MODEL, TERM_ID, should_run)

    return should_run, inventory


def _compile_inventory(
    cycles: list[dict],
    rng: Union[int, np.random.Generator, None] = None
) -> dict:
    """
    Build an annual inventory of model input data.

    Parameters
    ----------
    land_cover_nodes : list[dict]
        A list of HESTIA [Cycles](https://www.hestia.earth/schema/Cycle).
    seed : int | random.Generator | None
        The rng/seed for the random sampling of model parameters.

    Returns
    -------
    dict
        Annual inventory of model data.
    """
    COPY_FIELDS = ("startDate", "endDate")

    cycle_data = {
        cycle.get("@id"): {
            "biochar_nodes": filter_list_term_type(cycle.get("inputs", []), TermTermType.BIOCHAR),
            **{k: v for k in COPY_FIELDS if (v := cycle.get(k)) is not None}
        } for cycle in cycles
    }

    biochar_term_ids = sorted(reduce(
        lambda result, data: result.union(_get_unique_term_ids(data.get("biochar_nodes", []))),
        cycle_data.values(),
        set()
    ))

    factor_cache = {
        term_id: {
            "oc_content": _sample_oc_content(term_id, rng),
            "frac_remaining": _sample_frac_remaining(term_id, rng),
        } for term_id in biochar_term_ids
    }

    total_oc = {
        id: reduce(
            lambda result, node: result + _calc_total_oc(node, factor_cache),
            data.get("biochar_nodes", []),
            0
        ) for id, data in cycle_data.items()
    }

    grouped = group_nodes_by_year(
        [
            {
                "total_oc": total_oc.get(id, 0),
                **data
            } for id, data in cycle_data.items()
        ],
        include_spillovers=True
    )

    inventory = {
        year: reduce(
            lambda result, item: result + item.get("total_oc", 0) * item.get("fraction_of_node_duration", 0),
            data,
            0
        ) for year, data in grouped.items()
    }

    logs = {
        "factor_cache": factor_cache
    }

    return inventory, logs


def _get_unique_term_ids(nodes: list[dict]) -> set[str]:
    return set(node.get("term", {}).get("@id") for node in nodes)


def _sample_oc_content(term_id: str, rng):
    """
    Get an array of random samples based on the default organic carbon content of a biochar term.
    """
    node = {"term": {"@id": term_id, "termType": TermTermType.BIOCHAR.value}}

    oc_prop = get_node_property(node, "organicCarbonContent")
    mu = oc_prop.get("value")
    sigma = oc_prop.get("sd")

    return truncated_normal_1d((1, _ITERATIONS), mu/100, sigma/100, 0, 1, seed=rng) if (mu and sigma) else 0


def _sample_frac_remaining(term_id: str, rng):
    """
    Get an array of random samples based on the `FRAC_OC_REMAINING_100_YEARS` lookups of a biochar term.
    """
    term = {"@id": term_id, "termType": TermTermType.BIOCHAR.value}

    mu = get_lookup_value(term, LOOKUPS["biochar"][0])
    sigma = get_lookup_value(term, LOOKUPS["biochar"][1])

    return truncated_normal_1d((1, _ITERATIONS), mu, sigma, 0, 1, seed=rng) if (mu and sigma) else 0


def _calc_total_oc(biochar_node: dict, factor_cache: dict):
    """
    Calculate the total amount of stable organic carbon added to the soil from an application of biochar.
    """
    term_id = biochar_node.get("term", {}).get("@id")

    mass = get_node_value(biochar_node)
    oc_content = factor_cache.get(term_id, {}).get("oc_content", 0)
    frac_remaining = factor_cache.get(term_id, {}).get("frac_remaining", 0)

    return mass * oc_content * frac_remaining


def _format_inventory(inventory: dict) -> str:
    """
    Format the biochar inventory for logging as a table.
    """
    inventory_years = sorted(set(non_empty_list(years for years in inventory.keys())))

    should_run = inventory and len(inventory_years) > 0

    return log_as_table(
        {
            "year": year,
            "stable-oc-from-biochar": _format_factor(inventory.get(year))
        } for year in inventory_years
    ) if should_run else "None"


def _format_logs(logs: dict):
    """
    Format model logs. Format method selected based on dict key, with `_format_str` as fallback.
    """
    return {
        _format_str(key): _LOG_KEY_TO_FORMAT_FUNC.get(key, _format_str)(value) for key, value in logs.items()
    }


def _format_factor_cache(factor_cache: dict) -> str:
    """
    Format the SOC inventory for logging as a table.
    """
    should_run = factor_cache and len(factor_cache) > 0

    return log_as_table(
        {
            "term-id": term_id,
            **{_format_str(key): _format_factor(value) for key, value in factor_dict.items()}
        } for term_id, factor_dict in factor_cache.items()
    ) if should_run else "None"


def _format_factor(value) -> str:
    """
    Format a model factor. Method selected based on factor type (ndarray, int or float).
    """
    format_func = next(
        (func for type, func in _TYPE_TO_FORMAT_FUNC.items() if isinstance(value, type)),
        None
    )
    return format_func(value) if format_func else "None"


def _format_nd_array(value) -> str:
    return f"{np.mean(value):.3g} ± {np.std(value):.3g}"


def _format_number(value) -> str:
    return f"{value:.3g}"


_INVALID_CHARS = {"_", ":", ",", "="}
_REPLACEMENT_CHAR = "-"


def _format_str(value: str, *_) -> str:
    """Format a string for logging in a table. Remove all characters used to render the table on the front end."""
    return reduce(lambda x, char: x.replace(char, _REPLACEMENT_CHAR), _INVALID_CHARS, str(value))


_TYPE_TO_FORMAT_FUNC = {
    np.ndarray: _format_nd_array,
    (float, int): _format_number
}


_LOG_KEY_TO_FORMAT_FUNC = {
    "factor_cache": _format_factor_cache
}


def _run(
    inventory: dict
) -> list[dict]:
    """
    Calculate the annual biochar organic carbon stock based on an inventory of biochar application data.

    Parameters
    ----------
    inventory : dict
        The annual inventory of biochar data.

    Returns
    -------
    list[dict]
        A list of HESTIA [Measurement](https://www.hestia.earth/schema/Measurement) nodes with `term.@id` =
        `biocharOrganicCarbonPerHa`
    """

    start_year = min(inventory.keys()) - 1
    end_year = max(inventory.keys()) + 1

    def accumulate_oc(result, year):
        value = inventory.get(year, np.zeros((1, _ITERATIONS)))
        prev = result.get(year-1, np.zeros((1, _ITERATIONS)))

        updated = result | {year: value+prev}
        return updated

    accumlated_oc = reduce(accumulate_oc, range(start_year, end_year), {})

    dates = [f"{year}-12-31" for year in accumlated_oc]
    values = np.vstack(tuple(accumlated_oc.values()))

    descriptive_stats = calc_descriptive_stats(
        values,
        _STATS_DEFINITION,
        axis=1,     # Calculate stats rowwise.
        decimals=6  # Round values to the nearest milligram.
    )
    return [_measurement(dates, **descriptive_stats)]


def _measurement(
    dates: list[int],
    value: list[float],
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
        "dates": dates,
        "depthUpper": _DEPTH_UPPER,
        "depthLower": _DEPTH_LOWER,
        "methodClassification": _METHOD_CLASSIFICATION
    }
    measurement = _new_measurement(TERM_ID, MODEL) | {
        key: value for key, value in update_dict.items() if value is not None
    }
    return measurement
