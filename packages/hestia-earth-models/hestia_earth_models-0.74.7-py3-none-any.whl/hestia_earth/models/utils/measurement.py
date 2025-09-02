from collections import defaultdict
from collections.abc import Iterable
from functools import reduce
from statistics import mode, mean
from typing import Any, Optional, Union
from hestia_earth.schema import MeasurementMethodClassification, SchemaType, TermTermType
from hestia_earth.utils.model import linked_node, filter_list_term_type
from hestia_earth.utils.tools import non_empty_list, flatten, safe_parse_float, list_sum
from hestia_earth.utils.date import diff_in_days

from . import flatten_args
from .blank_node import most_relevant_blank_node_by_id
from .method import include_method
from .term import download_term, get_lookup_value


# TODO: verify those values
OLDEST_DATE = '1800'
SOIL_TEXTURE_IDS = ['sandContent', 'siltContent', 'clayContent']
MEASUREMENT_REDUCE = {
    'mean': lambda value: mean(value),
    'mode': lambda value: mode(value),
    'sum': lambda value: sum(value)
}

MEASUREMENT_METHOD_CLASSIFICATIONS = [e.value for e in MeasurementMethodClassification]


def _new_measurement(term, method=None):
    node = {'@type': SchemaType.MEASUREMENT.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_term(term))
    return include_method(node, term_id=method)


def measurement_value(measurement: dict, is_larger_unit: bool = False, default=None) -> float:
    term = measurement.get('term', {})
    reducer = get_lookup_value(term, 'arrayTreatmentLargerUnitOfTime' if is_larger_unit else 'arrayTreatment') or 'mean'
    value = non_empty_list(measurement.get('value', []))
    is_value_valid = value is not None and isinstance(value, list) and len(value) > 0
    return MEASUREMENT_REDUCE.get(reducer, lambda v: v[0])(value) if is_value_valid else default


def most_relevant_measurement_value(measurements: list, term_id: str, date: str, default=None):
    measurement = most_relevant_blank_node_by_id(measurements, term_id, date)
    return measurement_value(measurement, default=default) if measurement else default


def _group_measurement_key(measurement: dict, include_dates: bool = True):
    keys = non_empty_list([
        str(measurement.get('depthUpper', '')),
        str(measurement.get('depthLower', '')),
        measurement.get('startDate') if include_dates else None,
        measurement.get('endDate') if include_dates else None
    ])
    return '_to_'.join(keys) if len(keys) > 0 else 'no-depths'


def group_measurements_by_depth(measurements: list, include_dates: bool = True):
    def group_by(group: dict, measurement: dict):
        key = _group_measurement_key(measurement, include_dates)
        return group | {key: group.get(key, []) + [measurement]}

    return reduce(group_by, measurements, {})


def has_all_months(dates: list):
    try:
        months = [int(d[5:7]) for d in dates]
        return all(m in months for m in range(1, 13))
    except Exception:
        return False


def group_measurement_values_by_year(
    measurement: dict,
    inner_key: Union[Any, None] = None,
    complete_years_only: bool = False,
) -> Union[dict, None]:
    """
    Groups the values of a monthly measurement by year.

    Only complete years (i.e. where all 12 months have a value) are returned and values are
    not transformed in any way (i.e. they are not averaged).

    Parameters
    ----------
    measurement : dict
        A HESTIA `Measurement` node, see: https://www.hestia.earth/schema/Measurement.
    inner_key: Any | None
        An optional inner dictionary key for the outputted annualised groups (can be used to merge annualised
        dictionaries together), default value: `None`.
    complete_years_only : bool
        Keep only years where there is a measurement value for each calendar month, default value: `False`.

    Returns
    -------
    dict | None
        The annualised dictionary of measurement values by year.
    """
    dates = measurement.get('dates', [])
    values = measurement.get('value', [])

    def group_values(groups: dict, index: int) -> dict:
        """
        Reducer function used to group the `Measurement` dates and values into years.
        """
        try:
            date = dates[index]
            value = values[index]
            year = int(date[0:4])  # Get the year from a date in the format `YYYY-MM-DD`
            groups[year] = groups.get(year, []) + [(date, value)]
        except (IndexError, ValueError):
            pass
        return groups

    grouped = reduce(group_values, range(0, len(dates)), dict())

    iterated = {
        key: {inner_key: [v for _d, v in values]} if inner_key else [v for _d, v in values]
        for key, values in grouped.items()
        if has_all_months([d for d, _v in values]) or not complete_years_only
    }

    return iterated


def most_relevant_measurement_value_by_depth_and_date(
    measurements: list[dict],
    term_id: str,
    date: str,
    depth_upper: int,
    depth_lower: int,
    depth_strict: bool = True,
    default: Union[Any, None] = None
) -> Union[tuple[float, str], tuple[Any, None]]:
    """
    Returns the measurement value with the closest data, depth upper and depth lower.

    Parameters
    ----------
    measurements list[dict]
        A list of HESTIA `Measurement` nodes, see: https://www.hestia.earth/schema/Measurement.
    term_id : str
        The `@id` of a HESTIA `Term`. Example: `"sandContent"`
    date : str
        The target date in ISO 8601 string format (`"YYYY-MM-DD"`), see: https://en.wikipedia.org/wiki/ISO_8601.
    depth_upper : int
        The target `depthUpper` of the `Measurement`.
    depth_lower : int
        The target `depthLower` of the `Measurement`.
    depth_strict : bool
        Whether or not the depth requirement is strict, default value: `True`.
    default : Any | None
        The returned value if no match was found, default value: `None`.

    Returns
    -------
    tuple[float, str] | tuple[Any, None]:
        If a nearest measurement is found, return `(nearest_value, nearest_date)` else return `(default, None)`
    """
    filtered_measurements = [m for m in measurements if m.get('term', {}).get('@id') == term_id]

    if len(filtered_measurements) == 0:
        return default, None

    grouped_measurements = group_measurements_by_depth(filtered_measurements, False)

    def depth_distance(depth_string):
        split = depth_string.split('_')
        upper, lower = safe_parse_float(split[0], default=0), safe_parse_float(split[2], default=0)  # "a_to_b"
        return abs(upper - depth_upper) + abs(lower - depth_lower)

    nearest_key = min(grouped_measurements.keys(), key=depth_distance)
    closest_depth_measurements = (
        grouped_measurements.get(nearest_key, []) if depth_distance(nearest_key) <= 0 or not depth_strict else []
    )

    dates = flatten([measurement.get('dates', []) for measurement in closest_depth_measurements])
    values = flatten([measurement.get('value', []) for measurement in closest_depth_measurements])

    def date_distance(_date):
        return abs(diff_in_days(_date if _date else OLDEST_DATE, date))

    nearest_value, nearest_date = min(zip(values, dates), key=lambda i: date_distance(i[1]), default=(default, None))

    return nearest_value, nearest_date


_MEASUREMENT_METHOD_CLASSIFICATION_RANKING = [
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS,
    MeasurementMethodClassification.TIER_3_MODEL,
    MeasurementMethodClassification.TIER_2_MODEL,
    MeasurementMethodClassification.TIER_1_MODEL,
    MeasurementMethodClassification.PHYSICAL_MEASUREMENT_ON_NEARBY_SITE,
    MeasurementMethodClassification.GEOSPATIAL_DATASET,
    MeasurementMethodClassification.REGIONAL_STATISTICAL_DATA,
    MeasurementMethodClassification.COUNTRY_LEVEL_STATISTICAL_DATA,
    MeasurementMethodClassification.EXPERT_OPINION,
    MeasurementMethodClassification.UNSOURCED_ASSUMPTION
]
"""
A ranking of `MeasurementMethodClassification`s from strongest to weakest.
"""

_MeasurementMethodClassifications = Union[
    MeasurementMethodClassification, str, Iterable[Union[MeasurementMethodClassification, str]]
]
"""
A type alias for a single measurement method classification, as either an MeasurementMethodClassification enum or
string, or multiple measurement method classification, as either an iterable of MeasurementMethodClassification enums
or strings.
"""


def min_measurement_method_classification(
    *methods: _MeasurementMethodClassifications
) -> MeasurementMethodClassification:
    """
    Get the minimum ranking measurement method from the provided methods.

    n.b., `max` function is used as weaker methods have higher indices.

    Parameters
    ----------
    *methods : MeasurementMethodClassification | str | Iterable[MeasurementMethodClassification] | Iterable[str]
        Measurement method classifications or iterables of measurement method classification.

    Returns
    -------
    MeasurementMethodClassification
        The measurement method classification with the minimum ranking.
    """
    methods_ = [to_measurement_method_classification(arg) for arg in flatten_args(methods)]
    return max(
        methods_,
        key=lambda method: _MEASUREMENT_METHOD_CLASSIFICATION_RANKING.index(method),
        default=_MEASUREMENT_METHOD_CLASSIFICATION_RANKING[-1]
    )


def to_measurement_method_classification(
    method: Union[MeasurementMethodClassification, str]
) -> Optional[MeasurementMethodClassification]:
    """
    Convert the input to a `MeasurementMethodClassification` if possible.

    Parameters
    ----------
    method : MeasurementMethodClassification | str
        The measurement method as either a `str` or `MeasurementMethodClassification`.

    Returns
    -------
    MeasurementMethodClassification | None
        The matching `MeasurementMethodClassification` or `None` if invalid string.
    """
    return (
        method if isinstance(method, MeasurementMethodClassification)
        else MeasurementMethodClassification(method) if method in MEASUREMENT_METHOD_CLASSIFICATIONS
        else None
    )


def group_measurements_by_method_classification(
    nodes: list[dict]
) -> dict[MeasurementMethodClassification, list[dict]]:
    """
    Group [Measurement](https://www.hestia.earth/schema/Measurement) nodes by their method classification.

    The returned dict has the shape:
    ```
    {
        method (MeasurementMethodClassification): nodes (list[dict]),
        ...methods
    }
    ```

    Parameters
    ----------
    nodes : list[dict]
        A list of Measurement nodes.

    Returns
    -------
    dict[MeasurementMethodClassification, list[dict]]
        The measurement nodes grouped by method classification.
    """
    valid_nodes = (node for node in nodes if node.get("@type") == SchemaType.MEASUREMENT.value)

    def group_node(groups: dict, node: dict) -> list[dict]:
        measurement_method_classification = MeasurementMethodClassification(node.get("methodClassification"))
        groups[measurement_method_classification].append(node)
        return groups

    grouped_nodes = reduce(group_node, valid_nodes, defaultdict(list))
    return dict(grouped_nodes)


def total_other_soilType_value(measurements: list, term_id: str):
    sum_group = get_lookup_value({'@id': term_id, 'termType': TermTermType.SOILTYPE.value}, 'sumMax100Group')
    measurements = [
        m for m in filter_list_term_type(measurements, TermTermType.SOILTYPE)
        if all([
            get_lookup_value(m.get('term'), 'sumMax100Group') == sum_group,
            m.get('depthUpper', 0) == 0,
            m.get('depthLower', 0) == 30
        ])
    ]
    return list_sum([list_sum(m.get('value') or []) for m in measurements])
