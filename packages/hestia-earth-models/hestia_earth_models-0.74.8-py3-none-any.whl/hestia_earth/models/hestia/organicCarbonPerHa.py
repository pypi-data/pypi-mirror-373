from typing import Optional, Union

from hestia_earth.schema import MeasurementMethodClassification
from hestia_earth.utils.date import diff_in_days
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import flatten, non_empty_list, safe_parse_float

from hestia_earth.models.log import log_as_table, logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import _get_last_date, group_nodes_by_last_date, node_term_match
from hestia_earth.models.utils.measurement import (
    _new_measurement, group_measurements_by_depth, measurement_value, OLDEST_DATE
)
from hestia_earth.models.utils.source import get_source
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [
            {
                "@type": "Measurement",
                "value": "",
                "term.@id": "soilBulkDensity",
                "depthUpper": "",
                "depthLower": "",
                "methodClassification": ["on-site physical measurement", "modelled using other measurements"]
            },
            {
                "@type": "Measurement",
                "value": "",
                "dates": "",
                "term.@id": "organicCarbonPerKgSoil",
                "depthUpper": "",
                "depthLower": "",
                "methodClassification": ["on-site physical measurement", "modelled using other measurements"]
            }
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "dates": "",
        "depthUpper": "",
        "depthLower": "",
        "methodClassification": "modelled using other measurements"
    }]
}
TERM_ID = 'organicCarbonPerHa'
BIBLIO_TITLE = 'Soil organic carbon sequestration rates in vineyard agroecosystems under different soil management practices: A meta-analysis'  # noqa: E501
RESCALE_DEPTH_UPPER = 0
RESCALE_DEPTH_LOWER = 30

# --- UTILS ---

MAX_DEPTH_LOWER = 100
SOIL_BULK_DENSITY_TERM_ID = 'soilBulkDensity'
ORGANIC_CARBON_PER_KG_SOIL_TERM_ID = 'organicCarbonPerKgSoil'
VALID_MEASUREMENT_METHOD_CLASSIFICATIONS = {
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT.value,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
}


def _measurement(
    site: dict, value: float, depthUpper: Union[int, float], depthLower: Union[int, float], date: Optional[str] = None
) -> dict:
    data = _new_measurement(TERM_ID, MODEL)
    data['value'] = [value]
    data['depthUpper'] = int(depthUpper)
    data['depthLower'] = int(depthLower)
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS.value
    if date is not None:
        data['dates'] = [date]
    return data | get_source(site, BIBLIO_TITLE)


# --- CALCULATE `organicCarbonPerHa` ---


def _calc_organic_carbon_per_ha(
    depth_upper: float,
    depth_lower: float,
    soil_bulk_density: float,
    organic_carbon_per_kg_soil: float
) -> float:
    """
    Calculate `organicCarbonPerHa` from `soilBulkDensity` and `organicCarbonPerKgSoil` using method adapted from
    [Payen et al (2021)](https://doi.org/10.1016/j.jclepro.2020.125736).

    Parameters
    ----------
    depth_upper : float
        Measurement depth upper in centimetres (min `0`).
    depth_lower : float,
        Measurement depth upper in centimetres (min `0`).
    soil_bulk_density : float,
        Soil bulk density between depth upper and depth lower, Mg soil m-3
    organic_carbon_per_kg_soil : float
        Soil organic carbon concentration between depth upper and depth lower, kg C kg soil-1

    Return
    ------
    float
        The SOC stock per hectare within the specified depth interval, kg C ha-1.
    """
    return (depth_lower - depth_upper) * soil_bulk_density * organic_carbon_per_kg_soil * 100


def _should_run_calculation(site: dict) -> tuple[bool, dict[str, list[dict]]]:
    """
    Pre-process site data and determine whether there is sufficient data to calculate `organicCarbonPerHa`.
    """
    oc_nodes = [node for node in site.get("measurements", []) if _valid_measurement(node, TERM_ID)]

    # We don't need to run the model for any dates we already have an `organicCarbonPerHa` value for.
    oc_node_dates = set(non_empty_list(flatten(measurement.get("dates", []) for measurement in oc_nodes)))

    occ_nodes = [
        node for node in site.get("measurements", [])
        if all([
            _valid_measurement(node, ORGANIC_CARBON_PER_KG_SOIL_TERM_ID),
            len(node.get("dates", [])) > 0,
            _get_last_date(node.get("dates", [])) not in oc_node_dates
        ])
    ]

    bd_nodes = [node for node in site.get("measurements", []) if _valid_measurement(node, SOIL_BULK_DENSITY_TERM_ID)]

    measurements = occ_nodes + bd_nodes
    grouped_measurements = group_measurements_by_depth(measurements, include_dates=False)

    inventory = {
        depth_key: {
            "measurements": nodes,
            "has-soil-bulk-density": bool(find_term_match(nodes, SOIL_BULK_DENSITY_TERM_ID)),
            "has-organic-carbon-per-kg-soil": bool(find_term_match(nodes, SOIL_BULK_DENSITY_TERM_ID))
        } for depth_key, nodes in grouped_measurements.items()
    }

    valid_grouped_measurements = {
        depth_key: group["measurements"] for depth_key, group in inventory.items()
        if all([group["has-soil-bulk-density"], group["has-organic-carbon-per-kg-soil"]])
    }

    should_run = bool(valid_grouped_measurements)

    logs = {
        "should_run_calculation": should_run,
        "inventory_calculation": log_as_table(
            {
                "depth-key": str(depth_key).replace("_", "-"),
                "should-run": depth_key in valid_grouped_measurements,
                "has-soil-bulk-density": group["has-soil-bulk-density"],
                "has-organic-carbon-per-kg-soil": group["has-organic-carbon-per-kg-soil"]
            } for depth_key, group in inventory.items()
        ) if inventory else "None"
    }

    return should_run, valid_grouped_measurements, logs


def _valid_measurement(node: dict, target_term_id: str) -> bool:
    return all([
        node_term_match(node, target_term_id),
        node.get("value"),
        node.get("depthLower") is not None,
        node.get("depthUpper") is not None,
        node.get("methodClassification") in VALID_MEASUREMENT_METHOD_CLASSIFICATIONS
    ])


def _run_calculation(site: dict, depth_key: str, measurement_nodes: list[dict]) -> list[dict]:
    """
    Returns an `organicCarbonPerHa` measurement node for each `organicCarbonPerKgSoil` node in depth group using the
    most relevant `soilBulkDensity` node available.

    Parameters
    ----------
    site : dict
        A [Site node](https://www.hestia.earth/schema/Site).
    depth_key : str
        A depth key in the format `"a_to_b"`.
    measurement_nodes : list[dict]
        A list of pre-validated [Measurement nodes](https://www.hestia.earth/schema/Measurement).

    Return
    ------
    list[dict]
        A list of `organicCarbonPerHa` [Measurement nodes](https://www.hestia.earth/schema/Measurement).
    """
    split = depth_key.split('_')  # "a_to_b"
    depth_upper = safe_parse_float(split[0], default=0)
    depth_lower = safe_parse_float(split[2], default=0)

    soil_bulk_density_nodes = [
        node for node in measurement_nodes if node.get('term', {}).get('@id') == SOIL_BULK_DENSITY_TERM_ID
    ]

    organic_carbon_per_kg_soil_nodes = [
        node for node in measurement_nodes if node.get('term', {}).get('@id') == ORGANIC_CARBON_PER_KG_SOIL_TERM_ID
    ]

    dates = [_get_last_date(node.get('dates', [])) for node in organic_carbon_per_kg_soil_nodes]

    def closest_bd(datestr: str):
        """
        Returns the `soilBulkDensity` node closest to target datestr. `nodes` input are pre-validated to always contain
        at least one `soilBulkDensity` node.
        """
        return next(
            iter(sorted(
                soil_bulk_density_nodes,
                key=lambda node: abs(diff_in_days(
                    _get_last_date(node.get('dates', [])) or OLDEST_DATE,
                    datestr or OLDEST_DATE
                ))
            ))
        )

    values = [
        _calc_organic_carbon_per_ha(
            depth_upper,
            depth_lower,
            measurement_value(closest_bd(datestr)),
            measurement_value(organic_carbon_per_kg_soil_node)
        ) for organic_carbon_per_kg_soil_node, datestr in zip(organic_carbon_per_kg_soil_nodes, dates)
    ]

    return [_measurement(site, value, depth_upper, depth_lower, datestr) for value, datestr in zip(values, dates)]


# --- RESCALE `organicCarbonPerHa` ---


def _c_to_depth(d: float) -> float:
    """
    The definite integral of `c_density_at_depth` between `0` and `d`.

    Parameters
    ----------
    d : float
        Measurement depth in metres (min `0`, max `1`).

    Returns
    -------
    float
        The carbon stock per m2 to depth `d`, kg C-2.
    """
    return 22.1 * d - (33.3 * pow(d, 2)) / 2 + (14.9 * pow(d, 3)) / 3


def _cdf(depth_upper: float, depth_lower: float) -> float:
    """
    The ratio between the carbon stock per m2 to depth `d` and the carbon stock per m2 to depth `1`.

    Parameters
    ----------
    depth_upper : float
        Measurement depth upper in metres (min `0`, max `1`).
    depth_lower : float
        Measurement depth lower in metres (min `0`, max `1`).

    Returns
    -------
    float
        The proportion of carbon stored between `depth_upper` and `depth_lower` compared to between `0` and `1` metres.
    """
    return (_c_to_depth(depth_lower) - _c_to_depth(depth_upper)) / _c_to_depth(1)


def _rescale_soc_value(
    source_value: float,
    source_depth_upper: float,
    source_depth_lower: float,
    target_depth_upper: float,
    target_depth_lower: float
) -> float:
    """
    Rescale an SOC measurement value from a source depth interval to a target depth interval.

    Depths are converted from centimetres (HESTIA schema) to metres for use in `cdf` function.

    Parameters
    ----------
    source_value : float
        Source SOC stock (kg C ha-1).
    source_depth_upper : float
        Source measurement depth upper in centimetres (min `0`, max `100`).
    source_depth_lower : float
        Source measurement depth lower in centimetres, must be greater than `source_depth_upper` (min `0`, max `100`).
    target_depth_upper : float
        Target measurement depth upper in centimetres (min `0`, max `100`).
    target_depth_lower : float
        Target measurement depth lower in centimetres, must be greater than `target_depth_upper` (min `0`, max `100`).

    Returns
    -------
    float
        The estimated SOC stock for the target depth interval (kg C ha-1).
    """
    cd_target = _cdf(target_depth_upper/100, target_depth_lower/100)
    cd_measurement = _cdf(source_depth_upper/100, source_depth_lower/100)
    return source_value * (cd_target / cd_measurement)


def _should_run_rescale_node(node: list) -> bool:
    """
    Validate that a node has `depthUpper` = `0` and a `depthLower` < `100`.
    """
    return all([
        node.get('depthUpper', 1) == RESCALE_DEPTH_UPPER,
        node.get('depthLower', 101) <= MAX_DEPTH_LOWER
    ])


def _should_run_rescale_group(nodes: list) -> bool:
    """
    Validate that a list of nodes doesn't contain a node with `depthUpper` = `0` and a `depthLower` < `30`.
    """
    return not any([
        node for node in nodes if all([
            node.get('depthUpper', 1) == RESCALE_DEPTH_UPPER,
            node.get('depthLower', 101) == RESCALE_DEPTH_LOWER
        ])
    ])


def _should_run_rescale(organic_carbon_per_ha_nodes: list) -> tuple[bool, dict[str, list[dict]]]:
    """
    Pre-process `organicCarbonPerHa` nodes and determine whether any need to be rescaled to a depth interval of 0-30cm.
    """
    grouped_nodes = group_nodes_by_last_date(
        [node for node in organic_carbon_per_ha_nodes if _should_run_rescale_node(node)]
    )

    valid_grouped_nodes = {
        datestr: nodes for datestr, nodes in grouped_nodes.items()
        if _should_run_rescale_group(nodes)
    }

    should_run = bool(valid_grouped_nodes)

    logs = {
        "should_run_rescale": should_run,
        "inventory_rescale": log_as_table(
            {
                "date": str(datestr),
                "should-run": datestr in valid_grouped_nodes.keys()
            } for datestr in grouped_nodes.keys()
        ) if grouped_nodes else "None"
    }

    return should_run, valid_grouped_nodes, logs


def _depth_distance(node: dict):
    return abs(node.get('depthLower', 101) - RESCALE_DEPTH_LOWER)


def _get_most_relevant_soc_node(organic_carbon_per_ha_nodes: list[dict]):
    """
    Find the `organic_carbon_per_ha_node` with the closest depth interval to 0 - 30cm. `depthLowers` greater than 30cm
    are prioritised. Returns `{}` if input list is empty.
    """
    priority_nodes = [
        node for node in organic_carbon_per_ha_nodes
        if 'depthLower' in node and node.get('depthLower') >= RESCALE_DEPTH_LOWER
    ]
    nodes = priority_nodes or organic_carbon_per_ha_nodes  # If priority nodes are available use them.

    return next(node for node in nodes if _depth_distance(node) == min(_depth_distance(node) for node in nodes))


def _run_rescale(site: dict, organic_carbon_per_ha_nodes: list[dict]) -> list[dict]:
    """
    For each unique measurement date, rescale the deepest `organicCarbonPerHa` node to a depth of 0 to 30cm.
    """
    node = _get_most_relevant_soc_node(organic_carbon_per_ha_nodes)

    value = _rescale_soc_value(
        measurement_value(node),
        RESCALE_DEPTH_UPPER, node.get('depthLower'),
        RESCALE_DEPTH_UPPER, RESCALE_DEPTH_LOWER,
    ) if node else None
    date = _get_last_date(node.get("dates", [])) if node else None

    return _measurement(site, value, RESCALE_DEPTH_UPPER, RESCALE_DEPTH_LOWER, date) if value is not None else []


# --- RUN MODEL ---


def run(site: dict):
    should_run_calculation, grouped_measurements, logs_calculation = _should_run_calculation(site)
    result_calculation = (
        flatten([_run_calculation(site, depth_key, nodes) for depth_key, nodes in grouped_measurements.items()])
        if should_run_calculation else []
    )

    oc_per_ha_nodes = (
        result_calculation + [m for m in site.get('measurements', []) if m.get('term', {}).get('@id') == TERM_ID]
    )

    should_run_rescale, grouped_oc_per_ha_nodes, logs_rescale = _should_run_rescale(oc_per_ha_nodes)
    result_rescale = (
        [_run_rescale(site, nodes) for nodes in grouped_oc_per_ha_nodes.values()]
        if should_run_rescale else []
    )

    logRequirements(site, model=MODEL, term=TERM_ID, **logs_calculation, **logs_rescale)
    logShouldRun(site, MODEL, TERM_ID, should_run=should_run_calculation or should_run_rescale)

    return result_calculation + result_rescale
