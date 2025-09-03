from calendar import monthrange
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime, timedelta
from enum import Enum
from functools import reduce
from typing import (
    Any,
    List,
    Callable,
    NamedTuple,
    Optional,
    Union
)
from dateutil import parser
from dateutil.relativedelta import relativedelta
from hestia_earth.schema import TermTermType
from hestia_earth.utils.blank_node import ArrayTreatment, get_node_value
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import (
    flatten,
    list_sum,
    list_average,
    safe_parse_date,
    non_empty_list
)
from hestia_earth.utils.lookup_utils import (
    is_model_siteType_allowed,
    is_model_product_id_allowed,
    is_siteType_allowed,
    is_product_id_allowed,
    is_product_termType_allowed,
    is_input_id_allowed,
    is_input_termType_allowed
)

from hestia_earth.models.log import debugValues, log_as_table
from . import is_from_model, _filter_list_term_unit, is_iterable, full_date_str
from .constant import Units, get_atomic_conversion
from .lookup import _node_value
from .property import get_node_property, get_node_property_value
from .term import get_lookup_value, download_term

# TODO: verify those values
MAX_DEPTH = 1000
OLDEST_DATE = '1800'


def group_by_term(values: list):
    def group_by(groups: dict, value: dict):
        key = value.get('term', {}).get('@id')
        groups[key] = groups.get(key, []) + [value]
        return groups
    return reduce(group_by, values, {})


def merge_blank_nodes(source: list, new_values: list):
    """
    Merge a list of blank nodes into an existing list of blank nodes.
    Warning: we only consider the `term.@id` here, and not the full list of properties that make the nodes unique.
    This should only be used when merging simple list of nested blank nodes.
    """
    for new_value in non_empty_list(new_values):
        term_id = new_value.get('term', {}).get('@id')
        index = next(
            (i for i, data in enumerate(source) if data.get('term', {}).get('@id') == term_id),
            None
        )
        if index is None:
            source.append(new_value)
        else:
            source[index] = source[index] | new_value
    return source


def lookups_logs(model: str, blank_nodes: list, lookups_per_termType: dict, **log_args):
    def mapper(blank_node: dict):
        term = blank_node.get('term', {})
        term_id = term.get('@id')
        term_type = term.get('termType')
        lookups = lookups_per_termType.get(term_type, [])
        lookups = lookups if isinstance(lookups, list) else [lookups]

        def _reduce_lookups_logs(logs: dict, column: str):
            lookup_value = get_lookup_value(term, column, model=model, **log_args)
            return logs | {column: str(lookup_value).replace(':', '-')}

        return reduce(_reduce_lookups_logs, lookups, {'id': term_id})

    logs = list(map(mapper, blank_nodes))

    return log_as_table(logs)


def properties_logs(blank_nodes: list, properties: Union[dict, list]):
    def mapper(blank_node: dict):
        term = blank_node.get('term', {})
        term_id = term.get('@id')
        term_type = term.get('termType')
        props = properties.get(term_type, []) if isinstance(properties, dict) else properties
        props = props if isinstance(props, list) else [props]

        def _reduce_properties_logs(logs: dict, prop: str):
            value = get_node_property(blank_node, prop).get('value')
            return logs | {prop: value}

        return reduce(_reduce_properties_logs, properties, {'id': term_id})

    logs = list(map(mapper, blank_nodes))

    return log_as_table(logs)


def _module_term_id(term_id: str, module):
    term_id_str = term_id.split('.')[-1] if '.' in term_id else term_id
    return getattr(module, 'TERM_ID', term_id_str).split(',')[0]


def _run_model_required(model: str, term_id: str, data: dict, skip_logs: bool = False):
    siteType_allowed = is_model_siteType_allowed(model, term_id, data)
    product_id_allowed = is_model_product_id_allowed(model, term_id, data)

    run_required = all([siteType_allowed, product_id_allowed])
    if not skip_logs:
        debugValues(data, model=model, term=term_id,
                    run_required=run_required,
                    siteType_allowed=siteType_allowed,
                    product_id_allowed=product_id_allowed)
    return run_required


def _run_required(model: str, term_id: str, data: dict):
    siteType_allowed = is_siteType_allowed(data, term_id)
    product_id_allowed = is_product_id_allowed(data, term_id)
    product_termType_allowed = is_product_termType_allowed(data, term_id)
    input_id_allowed = is_input_id_allowed(data, term_id)
    input_termType_allowed = is_input_termType_allowed(data, term_id)

    run_required = all([
        siteType_allowed, product_id_allowed, product_termType_allowed, input_id_allowed, input_termType_allowed
    ])
    # model is only used for logs here, skip logs if model not provided
    if model:
        debugValues(data, model=model, term=term_id,
                    siteType_allowed=siteType_allowed,
                    product_id_allowed=product_id_allowed,
                    product_termType_allowed=product_termType_allowed,
                    input_id_allowed=input_id_allowed,
                    input_termType_allowed=input_termType_allowed)
        # logging this for the model would cause issues parsing statuses
        if not model.endswith('NotRelevant'):
            debugValues(data, model=model, term=term_id, run_required=run_required)
    return run_required


def is_run_required(model: str, term_id: str, node: dict):
    """
    Determines whether the term for the model should run or not, based on lookup values.

    Parameters
    ----------
    model : str
        The `@id` of the model. Example: `pooreNemecek2018`.
    term_id : str
        The `@id` of the `Term` or the full JSON-LD of the Term. Example: `sandContent`.
    node : dict
        The node on which the model is applied. Logging purpose ony.

    Returns
    -------
    bool
        True if the model is required to run.
    """
    return (
        (_run_model_required(model, term_id, node) if model else True) and _run_required(model, term_id, node)
    ) if term_id else True


def run_if_required(model: str, term_id: str, data: dict, module):
    return getattr(module, 'run')(data) if is_run_required(model, _module_term_id(term_id, module), data) else []


def find_terms_value(nodes: list, term_id: str, default: Union[int, None] = 0):
    """
    Returns the sum of all blank nodes in the list which match the `Term` with the given `@id`.

    Parameters
    ----------
    values : list
        The list in which to search for. Example: `cycle['nodes']`.
    term_id : str
        The `@id` of the `Term`. Example: `sandContent`

    Returns
    -------
    float
        The total `value` as a number.
    """
    return list_sum(get_total_value(filter(lambda node: node.get('term', {}).get('@id') == term_id, nodes)), default)


def has_gap_filled_by_ids(nodes: list, term_ids: List[str]):
    nodes = [n for n in nodes if n.get('term', {}).get('@id') in term_ids]
    return any([is_from_model(n) for n in nodes])


def has_original_by_ids(nodes: list, term_ids: List[str]):
    nodes = [n for n in nodes if n.get('term', {}).get('@id') in term_ids]
    return any([not is_from_model(n) for n in nodes])


def get_total_value(nodes: list):
    """
    Get the total `value` of a list of Blank Nodes.
    This method does not take into account the `units` and possible conversions.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    return list(map(lambda node: list_sum(node.get('value', []), None), nodes))


def _value_as(term_id: str, convert_to_property=True):
    def get_value(node: dict):
        factor = get_node_property_value(
            None, node, term_id, default=0, handle_percents=False
        ) or get_lookup_value(
            lookup_term=node.get('term', {}),
            column=term_id
        ) or 0
        # ignore node value if property is not found
        value = list_sum(node.get('value', []))
        property = get_node_property(node, term_id, find_default_property=False, download_from_hestia=True)
        ratio = factor / 100 if property.get('term', {}).get('units', '') == '%' else factor
        return 0 if ratio == 0 else (value * ratio if convert_to_property else value / ratio)
    return get_value


def get_total_value_converted(nodes: list, conversion_property: Union[List[str], str], convert_to_property=True):
    """
    Get the total `value` of a list of Blank Nodes converted using a property of each Blank Node.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.
    conversion_property : str|List[str]
        Property (or multiple properties) used for the conversion. Example: `nitrogenContent`.
        See https://hestia.earth/glossary?termType=property for a list of `Property`.
    convert_to_property : bool
        By default, property is multiplied on value to get result. Set `False` to divide instead.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    def convert_multiple(node: dict):
        value = 0
        for prop in conversion_property:
            value = _value_as(prop, convert_to_property)(node)
            node['value'] = [value]
        return value

    return [
        _value_as(conversion_property, convert_to_property)(node) if isinstance(conversion_property, str) else
        convert_multiple(node) for node in nodes
    ]


def get_total_value_converted_with_min_ratio(
    model: str, term: str, node: dict = {},
    blank_nodes: list = [],
    prop_id: str = 'energyContentHigherHeatingValue',
    min_ratio: float = 0.8,
    is_sum: bool = True
):
    values = [
        (
            blank_node.get('term', {}).get('@id'),
            list_sum(blank_node.get('value', [])),
            get_node_property_value(model, blank_node, prop_id)
        ) for blank_node in blank_nodes
    ]
    value_logs = log_as_table([{
        'node-id': term_id,
        'node-value': value,
        f"{prop_id}-value": prop_value
    } for term_id, value, prop_value in values])

    total_value = list_sum([value for term_id, value, prop_value in values])
    total_value_with_property = list_sum([value for term_id, value, prop_value in values if prop_value])
    total_value_ratio = total_value_with_property / total_value if total_value > 0 else 0

    logs = {
        f"{prop_id}-term-id": prop_id,
        f"{prop_id}-total-value": total_value,
        f"{prop_id}-total-value-with-property": total_value_with_property,
        f"{prop_id}-total-value-with-ratio": total_value_ratio,
        f"{prop_id}-min-value-ratio": min_ratio,
        f"{prop_id}-values": value_logs
    }

    debugValues(node, model=model, term=term,
                **logs)

    total_converted_value = list_sum([
        value * prop_value for term_id, value, prop_value in values if all([value, prop_value])
    ])

    return (
        total_converted_value * total_value / total_value_with_property if is_sum
        else total_converted_value / total_value_with_property
    ) if total_value_ratio >= min_ratio else None


def get_N_total(nodes: list) -> list:
    """
    Get the total nitrogen content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg N` will be used.
    2. Every blank node specified in `kg` or `kg dry matter` will be multiplied by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, [Units.KG, Units.KG_DRY_MATTER])
    return get_total_value(kg_N_nodes) + get_total_value_converted(kg_nodes, 'nitrogenContent')


def get_KG_total(nodes: list) -> list:
    """
    Get the total kg mass of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg` will be used.
    2. Every blank node specified in `kg N` will be divided by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_nodes) + get_total_value_converted(kg_N_nodes, 'nitrogenContent', False)


def get_P_total(nodes: list) -> list:
    """
    Get the total phosphorous content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node specified in `kg P` will be used.
    1. Every blank node specified in `kg N` will be multiplied by the `phosphateContentAsP` property.
    2. Every blank node specified in `kg` will be multiplied by the `phosphateContentAsP` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The phosphorous values as a list of numbers.
    """
    kg_P_nodes = _filter_list_term_unit(nodes, Units.KG_P)
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_P_nodes) + get_total_value_converted(kg_N_nodes + kg_nodes, 'phosphateContentAsP')


def get_P2O5_total(nodes: list) -> list:
    """
    Get the total phosphate content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node specified in `kg P2O5` will be used.
    1. Every blank node specified in `kg N` will be multiplied by the `phosphateContentAsP2O5` property.
    2. Every blank node specified in `kg` will be multiplied by the `phosphateContentAsP2O5` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The phosphate values as a list of numbers.
    """
    kg_P2O5_nodes = _filter_list_term_unit(nodes, Units.KG_P2O5)
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_P2O5_nodes) + get_total_value_converted(kg_N_nodes + kg_nodes, 'phosphateContentAsP2O5')


def convert_to_nitrogen(node: dict, model: str, blank_nodes: list, **log_args):
    def fallback_value(input: dict):
        value = get_node_property_value(model, input, 'crudeProteinContent', default=None, **log_args)
        return None if value is None else value / 6.25

    def prop_value(input: dict):
        value = get_node_property_value(model, input, 'nitrogenContent', default=None, **log_args)
        return value if value is not None else fallback_value(input)

    values = [(i, prop_value(i)) for i in blank_nodes]
    missing_nitrogen_property = [i.get('term', {}).get('@id') for i, value in values if value is None]

    debugValues(node, model=model,
                conversion_details=log_as_table([
                    {
                        'id': i.get('term', {}).get('@id'),
                        'value': list_sum(i.get('value', [])),
                        'nitrogenContent': value
                    }
                    for i, value in values
                ]),
                missing_nitrogen_property=';'.join(set(missing_nitrogen_property)),
                **log_args)

    return list_sum([
        list_sum(i.get('value', [])) * p_value for i, p_value in values if p_value is not None
    ]) if len(missing_nitrogen_property) == 0 else None


def convert_to_carbon(node: dict, model: str, blank_nodes: list, **log_args):
    def prop_value(input: dict):
        value = get_node_property_value(model, input, 'carbonContent', default=None, **log_args)
        return value or \
            get_node_property_value(model, input, 'energyContentHigherHeatingValue', default=0, **log_args) * 0.021

    values = [(i, prop_value(i)) for i in blank_nodes]
    missing_carbon_property = [i.get('term', {}).get('@id') for i, p_value in values if not p_value]

    debugValues(node, model=model,
                missing_carbon_property=';'.join(missing_carbon_property),
                **log_args)

    return list_sum([
        list_sum(i.get('value', [])) * p_value for i, p_value in values if p_value is not None
    ]) if len(missing_carbon_property) == 0 else None


def _convert_to_set(
    variable: Union[Iterable[Any], Any]
) -> set:
    """
    Description of function

    Parameters
    ----------
    variable : Iterable[Any] | Any
        The input variable, which can be either an iterable or a single element.

    Returns
    -------
    set
        A set containing the elements of the input variable.
    """
    return set(variable) if is_iterable(variable) else {variable}


def node_term_match(
    node: dict,
    target_term_ids: Union[str, set[str]]
) -> bool:
    """
    Check if the term ID of the given node matches any of the target term IDs.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    target_term_ids : str | set[str]
        A single term ID or an set of term IDs to check against.

    Returns
    -------
    bool
        `True` if the term ID of the node matches any of the target
        term IDs, `False` otherwise.

    """
    target_term_ids = _convert_to_set(target_term_ids)
    return node.get('term', {}).get('@id', None) in target_term_ids


def node_lookup_match(
    node: dict,
    lookup: str,
    target_lookup_values: Union[str, set[str]]
) -> bool:
    """
    Check if the lookup value in the node's term matches any of the
    target lookup values.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    lookup : str
        The lookup key.
    target_lookup_values : str | set[str]
        A single target lookup value or a set of target lookup values
        to check against.

    Returns
    -------
    bool
        `True` if there is a match, `False` otherwise.
    """
    target_lookup_values = _convert_to_set(target_lookup_values)
    return get_lookup_value(node.get('term', {}), lookup) in target_lookup_values


def cumulative_nodes_match(
    function: Callable[[dict], bool],
    nodes: list[dict],
    *,
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes that satisfy the provided
    function exceed the threshold.

    Parameters
    ----------
    function : Callable[[dict], bool]
        A function to determine whether a node should be included in
        the calculation.
    nodes : list[dict]
        The list of nodes to be considered.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the
        function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by
        default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit
        of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False`
        otherwise.

    """
    values = [
        get_node_value(
            node, key='value', is_larger_unit=is_larger_unit, array_treatment=array_treatment
        ) or default_node_value for node in nodes if function(node)
    ]

    return list_sum(non_empty_list(flatten(values))) > cumulative_threshold


def cumulative_nodes_term_match(
    nodes: list[dict],
    *,
    target_term_ids: Union[str, set[str]],
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes with matching term IDs
    exceed the threshold.

    Parameters
    ----------
    nodes : list[dict]
        The list of nodes to be considered.
    target_term_ids : str | set[str]
        The term ID or a set of term IDs to match.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False` otherwise.
    """
    target_term_ids = _convert_to_set(target_term_ids)

    def match_function(node: dict) -> bool:
        return node_term_match(node, target_term_ids)

    return cumulative_nodes_match(
        match_function,
        nodes,
        cumulative_threshold=cumulative_threshold,
        default_node_value=default_node_value,
        is_larger_unit=is_larger_unit,
        array_treatment=array_treatment
    )


def cumulative_nodes_lookup_match(
    nodes: list[dict],
    *,
    lookup: str,
    target_lookup_values: Union[str, set[str]],
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes with matching lookup values exceed the threshold.

    Parameters
    ----------
    nodes : list[dict]
        The list of nodes to be considered.
    lookup : str
        The lookup key to match against in the nodes.
    target_lookup_values : str | set[str]
        The lookup value or a set of lookup values to match.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the
        function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by
        default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit
        of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False`
        otherwise.
    """
    target_lookup_values = _convert_to_set(target_lookup_values)

    def match_function(node: dict) -> bool:
        return node_lookup_match(node, lookup, target_lookup_values)

    return cumulative_nodes_match(
        match_function,
        nodes,
        cumulative_threshold=cumulative_threshold,
        default_node_value=default_node_value,
        is_larger_unit=is_larger_unit,
        array_treatment=array_treatment
    )


# --- Blank Node date utils ---


class DatestrFormat(Enum):
    """
    Enum representing ISO date formats permitted by HESTIA.

    See: https://en.wikipedia.org/wiki/ISO_8601
    """
    YEAR = r"%Y"
    YEAR_MONTH = r"%Y-%m"
    YEAR_MONTH_DAY = r"%Y-%m-%d"
    YEAR_MONTH_DAY_HOUR_MINUTE_SECOND = r"%Y-%m-%dT%H:%M:%S"
    MONTH = r"--%m"
    MONTH_DAY = r"--%m-%d"


DATESTR_FORMAT_TO_EXPECTED_LENGTH = {
    DatestrFormat.YEAR: len("2001"),
    DatestrFormat.YEAR_MONTH: len("2001-01"),
    DatestrFormat.YEAR_MONTH_DAY: len("2001-01-01"),
    DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND: len("2001-01-01T00:00:00"),
    DatestrFormat.MONTH: len("--01"),
    DatestrFormat.MONTH_DAY: len("--01-01")
}


DatestrGapfillMode = Enum("DatestrGapfillMode", [
    "START",
    "MIDDLE",
    "END"
])
"""
Enum representing modes of gapfilling incomplete datestrings.
"""


DatetimeRange = NamedTuple(
    "DatetimeRange",
    [
        ("start", datetime),
        ("end", datetime)
    ]
)
"""
A named tuple for storing a datetime range.

Attributes
----------
start : datetime
    The start of the datetime range.
end : datetime
    The end of the datetime range.
"""


def _check_datestr_format(datestr: str, format: DatestrFormat) -> bool:
    """
    Use `datetime.strptime` to determine if a datestr is in a particular ISO format.
    """
    try:
        expected_length = DATESTR_FORMAT_TO_EXPECTED_LENGTH.get(format, 0)
        format_str = format.value
        parsed_datetime = datetime.strptime(datestr, format_str)
        return bool(parsed_datetime) and len(datestr) == expected_length
    except ValueError:
        return False


def _get_datestr_format(datestr: str, default: Optional[Any] = None) -> Union[DatestrFormat, Any, None]:
    """
    Check a datestr against each ISO format permitted by the HESTIA schema and
    return the matching format.
    """
    return next(
        (date_format for date_format in DatestrFormat if _check_datestr_format(str(datestr), date_format)),
        default
    )


def _gapfill_datestr_start(datestr: str, *_) -> str:
    """
    Gapfill an incomplete datestr with the earliest possible date and time.

    Datestr will snap to the start of the year/month/day as appropriate.
    """
    return datestr + "YYYY-01-01T00:00:00"[len(datestr):]


def _gapfill_datestr_end(datestr: str, format: DatestrFormat) -> str:
    """
    Gapfill an incomplete datestr with the latest possible date and time.

    Datestr will snap to the end of the year/month/day as appropriate.
    """
    datetime = safe_parse_date(datestr)
    num_days_in_month = (
        monthrange(datetime.year, datetime.month)[1]
        if datetime and format == DatestrFormat.YEAR_MONTH
        else 31
    )
    completion_str = f"YYYY-12-{num_days_in_month}T23:59:59"
    return datestr + completion_str[len(datestr):]


def _gapfill_datestr_middle(datestr: str, format: DatestrFormat) -> str:
    """
    Gap-fill an incomplete datestr with the middle value, halfway between the latest and earliest values.
    """
    start_date_obj = datetime.strptime(
        _gapfill_datestr_start(datestr),
        DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND.value
    )
    end_date_obj = datetime.strptime(
        _gapfill_datestr_end(datestr, format=format),
        DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND.value
    )
    middle_date = start_date_obj + (end_date_obj - start_date_obj) / 2
    return datetime.strftime(middle_date, DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND.value)


DATESTR_GAPFILL_MODE_TO_GAPFILL_FUNCTION = {
    DatestrGapfillMode.START: _gapfill_datestr_start,
    DatestrGapfillMode.MIDDLE: _gapfill_datestr_middle,
    DatestrGapfillMode.END: _gapfill_datestr_end
}


def _gapfill_datestr(datestr: str, mode: DatestrGapfillMode = DatestrGapfillMode.START) -> str:
    """
    Gapfill incomplete datestrs and returns them in the format `YYYY-MM-DDTHH:mm:ss`.
    """
    VALID_DATE_FORMATS = {
        DatestrFormat.YEAR, DatestrFormat.YEAR_MONTH, DatestrFormat.YEAR_MONTH_DAY
    }
    _datestr = str(datestr)
    format = _get_datestr_format(_datestr)
    should_run = format in VALID_DATE_FORMATS
    return DATESTR_GAPFILL_MODE_TO_GAPFILL_FUNCTION[mode](_datestr, format) if should_run else _datestr


def _str_dates_match(date_str_one: str, date_str_two: str, mode=DatestrGapfillMode.END) -> bool:
    """
    Comparison of non-gap-filled string dates.
    example: For end dates, '2010' would match '2010-12-31', but not '2010-01-01'
    """
    return (
        _gapfill_datestr(datestr=date_str_one, mode=mode) == _gapfill_datestr(datestr=date_str_two, mode=mode)
    )


def _datetime_within_range(datetime: datetime, range: DatetimeRange) -> bool:
    """
    Determine whether or not a `datetime` falls within a `DatetimeRange`.
    """
    return range.start <= datetime <= range.end


def _datetime_range_duration(range: DatetimeRange, add_second=False) -> float:
    """
    Determine the length of a `DatetimeRange` in seconds.

    Option to `add_second` to account for 1 second between 23:59:59 and 00:00:00
    """
    return (range.end - range.start).total_seconds() + int(add_second)


def _calc_datetime_range_intersection_duration(
    range_a: DatetimeRange, range_b: DatetimeRange, add_second=False
) -> float:
    """
    Determine the length of a `DatetimeRange` in seconds.

    Option to `add_second` to account for 1 second between 23:59:59 and 00:00:00
    """
    latest_start = max(range_a.start, range_b.start)
    earliest_end = min(range_a.end, range_b.end)

    intersection_range = DatetimeRange(
        start=latest_start,
        end=earliest_end
    )

    duration = _datetime_range_duration(intersection_range)

    # if less than 0 the ranges do not intersect, so return 0.
    return (
        _datetime_range_duration(intersection_range, add_second=add_second)
        if duration > 0 else 0
    )


# --- Group nodes by year ---


VALID_DATE_FORMATS_GROUP_NODES_BY_YEAR = {
    DatestrFormat.YEAR,
    DatestrFormat.YEAR_MONTH,
    DatestrFormat.YEAR_MONTH_DAY,
    DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
}


GroupNodesByYearMode = Enum("GroupNodesByYearMode", [
    "START_AND_END_DATE",
    "DATES"
])
"""
Enum representing modes of grouping nodes by year.

Members
-------
START_AND_END_DATE
    Use the `startDate` and `endDate` fields of the node.
DATES
    Use the `dates` field of the node.
"""


def _should_run_node_by_end_date(node: dict) -> bool:
    """
    Validate nodes for `group_nodes_by_year` using the "startDate" and "endDate" fields.
    """
    return (
        _get_datestr_format(node.get("endDate")) in VALID_DATE_FORMATS_GROUP_NODES_BY_YEAR
        and validate_start_date_end_date(node)
    )


def _should_run_node_by_dates(node: dict) -> bool:
    """
    Validate nodes for `group_nodes_by_year` using the "dates" field.
    """
    value = node.get("value")
    dates = node.get("dates")
    return (
        value and dates and len(dates) > 0 and len(value) == len(dates)
        and all(_get_datestr_format(datestr) in VALID_DATE_FORMATS_GROUP_NODES_BY_YEAR for datestr in node.get("dates"))
    )


GROUP_NODES_BY_YEAR_MODE_TO_SHOULD_RUN_NODE_FUNCTION = {
    GroupNodesByYearMode.START_AND_END_DATE: _should_run_node_by_end_date,
    GroupNodesByYearMode.DATES: _should_run_node_by_dates
}


def _get_node_datetime_range_from_start_and_end_date(
    node: dict, default_node_duration: int = 1
) -> Union[DatetimeRange, None]:
    """
    Get the datetime range from a node's "startDate" and "endDate" fields.

    If "startDate" field is not available, a start date is calculated using the end date
    and `default_node_duration`.
    """
    end = safe_parse_date(_gapfill_datestr(node.get("endDate"), DatestrGapfillMode.END))
    start = (
        safe_parse_date(_gapfill_datestr(node.get("startDate"), DatestrGapfillMode.START))
        or end - relativedelta(years=default_node_duration, seconds=-1) if end else None
    )

    valid = isinstance(start, datetime) and isinstance(end, datetime)
    return DatetimeRange(start, end) if valid else None


def _get_node_datetime_range_from_dates(
    node: dict, **_
) -> Union[DatetimeRange, None]:
    """
    Get the datetime range from a node's "dates" field.
    """
    dates = node.get("dates")
    end = max(
        non_empty_list(
            safe_parse_date(_gapfill_datestr(datestr, DatestrGapfillMode.END)) for datestr in dates
        ), default=None
    )
    start = min(
        non_empty_list(
            safe_parse_date(_gapfill_datestr(datestr, DatestrGapfillMode.START)) for datestr in dates
        ), default=None
    )

    valid = isinstance(start, datetime) and isinstance(end, datetime)
    return DatetimeRange(start, end) if valid else None


GROUP_NODES_BY_YEAR_MODE_TO_GET_DATETIME_RANGE_FUNCTION = {
    GroupNodesByYearMode.START_AND_END_DATE: _get_node_datetime_range_from_start_and_end_date,
    GroupNodesByYearMode.DATES: _get_node_datetime_range_from_dates
}


def _build_time_fraction_dict(
    group_datetime_range: DatetimeRange,
    node_datetime_range: DatetimeRange
) -> dict:
    """
    Build a dictionary containing fractions of the year and node duration based on datetime ranges.

    This function calculates the duration of the group or year, the duration of the node, and the intersection
    duration between the two. It then computes the fractions of the year and node duration represented by the
    intersection. The results are returned in a dictionary.

    Parameters
    ----------
    group_datetime_range : DatetimeRange
        The datetime range representing the entire group or year.
    node_datetime_range : DatetimeRange
        The datetime range representing the node.

    Returns
    -------
    dict
        A dictionary containing "fraction_of_group_duration" and "fraction_of_node_duration".
    """
    group_duration = _datetime_range_duration(group_datetime_range, add_second=True)
    node_duration = _datetime_range_duration(node_datetime_range, add_second=True)

    intersection_duration = _calc_datetime_range_intersection_duration(
        node_datetime_range, group_datetime_range, add_second=True
    )

    fraction_of_group_duration = intersection_duration / group_duration if group_duration > 0 else 0
    fraction_of_node_duration = intersection_duration / node_duration if node_duration > 0 else 0

    return {
        "fraction_of_group_duration": fraction_of_group_duration,
        "fraction_of_node_duration": fraction_of_node_duration
    }


def _validate_time_fraction_dict(
    time_fraction_dict: dict,
    is_final_group: bool
) -> bool:
    """
    Return `True` if the the node intersections with a year group by
    more than 30% OR the year group represents more than 50% of a node's
    duration. Return `False` otherwise.

    This is to prevent cycles/managements being categorised into a year group
    when due to overlapping by just a few days. In these cases, nodes will only
    be counted in the year group if the majority of that node takes place in
    that year.
    """
    FRACTION_OF_GROUP_DURATION_THRESHOLD = 0.3
    FRACTION_OF_NODE_DURATION_THRESHOLD = 0.5

    return any([
        time_fraction_dict["fraction_of_group_duration"] > FRACTION_OF_GROUP_DURATION_THRESHOLD,
        time_fraction_dict["fraction_of_node_duration"] > FRACTION_OF_NODE_DURATION_THRESHOLD,
        is_final_group and time_fraction_dict["fraction_of_node_duration"] == FRACTION_OF_NODE_DURATION_THRESHOLD
    ])


def group_nodes_by_year(
    nodes: list[dict],
    default_node_duration: int = 1,
    sort_result: bool = True,
    include_spillovers: bool = False,
    inner_key: Union[Any, None] = None,
    mode: GroupNodesByYearMode = GroupNodesByYearMode.START_AND_END_DATE
) -> dict[int, list[dict]]:
    """
    Group nodes by year based on either their "startDate" and "endDate" fields or their
    "dates" field. Incomplete date strings are gap-filled automatically using `_gapfill_datestr`
    function.

    Parameters
    ----------
    nodes : list[dict]
        A list of nodes with start and end date information.
    default_node_duration : int, optional
        Default duration of a node years if start date is not available, by default 1.
    sort_result : bool, optional
        Flag to sort the result by year, by default True.
    include_spillovers : bool, optional
        If grouping by start and end date, flag to determine whether nodes should be included in year groups that they
        spill-over into. If `False` year groups will not include nodes that overlap with them by less than 30% of a
        year, unless it is the only year group it overlaps with. By default False.
    inner_key: Any | None
        An optional inner dictionary key for the outputted annualised groups (can be used to merge annualised
        dictionaries together), default value: `None`.
    mode : GroupNodesByYearMode, optional
        The mode to determine how nodes are grouped by year. Options are defined in `GroupNodesByYearMode`.

    Returns
    -------
    dict[int, list[dict]]
        A dictionary where keys are years and values are lists of nodes.
    """

    should_run_node = GROUP_NODES_BY_YEAR_MODE_TO_SHOULD_RUN_NODE_FUNCTION[mode]
    get_node_datetime_range = GROUP_NODES_BY_YEAR_MODE_TO_GET_DATETIME_RANGE_FUNCTION[mode]

    valid_nodes = non_empty_list(flatten(split_node_by_dates(node) for node in nodes if should_run_node(node)))

    def group_node(groups: dict, index: int):
        node = valid_nodes[index]

        node_datetime_range = get_node_datetime_range(
            node, default_node_duration=default_node_duration
        )

        range_start = node_datetime_range.start.year if node_datetime_range else 0
        range_end = node_datetime_range.end.year + 1 if node_datetime_range else 0

        for year in range(range_start, range_end):

            group_datetime_range = DatetimeRange(
                start=safe_parse_date(_gapfill_datestr(year, DatestrGapfillMode.START)),
                end=safe_parse_date(_gapfill_datestr(year, DatestrGapfillMode.END))
            )

            is_final_year = _datetime_within_range(node_datetime_range.end, group_datetime_range)

            time_fraction_dict = _build_time_fraction_dict(group_datetime_range, node_datetime_range)

            should_run = (
                mode == GroupNodesByYearMode.DATES
                or include_spillovers
                or _validate_time_fraction_dict(
                    time_fraction_dict,
                    is_final_year
                )
            )

            should_run and groups[year].append(
                node | time_fraction_dict
            )

        return groups

    grouped = reduce(group_node, range(len(valid_nodes)), defaultdict(list))

    iterated = {
        year: {inner_key: group} if inner_key else group
        for year, group in grouped.items()
    }

    return dict(sorted(iterated.items())) if sort_result else iterated


def split_node_by_dates(node: dict) -> list[dict]:
    """
    Split a node with an array-like `value` and `dates` with multiple elements into a list of nodes with a single
    `value` and `dates`. All other array-like node fields (`sd`, `min`, `max`,  and `observations`) will be also be
    split. Any other fields will be copied with no modifications.

    All split fields will still be array-like, but will only contain one element. Any array-like fields with a
    different number of elements to `value` will not be split.

    This function should only run on nodes with array-like `value` and `dates` (e.g., nodes with `@type` == `Emission`,
    `Input`,`Measurement`, `Practice` or `Product`).

    Parameters
    ----------
    node : dict
        A HESTIA blank node with array-like `value` and `dates` (and optional array-like fields `sd`, `min`, `max`, and
        `observations`).

    Returns
    -------
    list[dict]
        A list of nodes with single `value` and `dates`.
    """
    REQUIRED_KEYS = ["value", "dates"]
    OPTIONAL_KEYS = ["sd", "min", "max", "observations"]

    value = node.get("value", [])
    target_len = len(value) if isinstance(value, list) else -1

    def should_run_key(key: str) -> bool:
        item = node.get(key, [])
        return isinstance(item, list) and len(item) == target_len

    should_run = all([
        target_len > 0,
        all(should_run_key(key) for key in REQUIRED_KEYS)
    ])

    valid_keys = REQUIRED_KEYS + [key for key in OPTIONAL_KEYS if should_run_key(key)]

    def split(result: list[dict], index: int) -> list[dict]:
        update = {key: [node[key][index]] for key in valid_keys}
        result.append(node | update)
        return result

    return (
        sorted(reduce(split, range(len(value)), list()), key=lambda node: node.get("dates", []))
        if should_run else [node]
    )


def group_nodes_by_year_and_month(
    nodes: list[dict],
    default_node_duration: int = 1,
    sort_result: bool = True,
    inner_key: Union[Any, None] = None
) -> dict[int, list[dict]]:
    """
    Group nodes by year based on either their "startDate" and "endDate" fields. Incomplete date strings are gap-filled
    automatically using `_gapfill_datestr` function.

    Returns a dict in the shape:
    ```
    {
        year (int): {
            month (int): nodes (list[dict])  # for each month 1 - 12
        }
    }
    ```

    Parameters
    ----------
    nodes : list[dict]
        A list of nodes with start and end date information.
    default_node_duration : int, optional
        Default duration of a node years if start date is not available, by default 1.
    sort_result : bool, optional
        Flag to sort the result by year, by default True.
    inner_key: Any | None
        An optional inner dictionary key for the outputted annualised groups (can be used to merge annualised
        dictionaries together), default value: `None`.

    Returns
    -------
    dict[int, list[dict]]
        A dictionary where keys are years and values are lists of nodes.
    """
    valid_nodes = [node for node in nodes if _should_run_node_by_end_date(node)]

    def group_node(groups: dict, index: int):
        node = valid_nodes[index]

        node_datetime_range = _get_node_datetime_range_from_start_and_end_date(
            node, default_node_duration=default_node_duration
        )

        range_start = node_datetime_range.start.year if node_datetime_range else 0
        range_end = node_datetime_range.end.year + 1 if node_datetime_range else 0

        for year in range(range_start, range_end):
            for month in range(1, 13):

                datestr_incomplete = f"{year}-{month:02}"
                group_datetime_range = DatetimeRange(
                    start=safe_parse_date(_gapfill_datestr(datestr_incomplete, DatestrGapfillMode.START)),
                    end=safe_parse_date(_gapfill_datestr(datestr_incomplete, DatestrGapfillMode.END))
                )

                is_final_month = _datetime_within_range(node_datetime_range.end, group_datetime_range)
                time_fraction_dict = _build_time_fraction_dict(group_datetime_range, node_datetime_range)
                should_run = _validate_time_fraction_dict(time_fraction_dict, is_final_month)

                should_run and groups[year][month].append(node)

        return groups

    grouped = reduce(group_node, range(len(valid_nodes)), defaultdict(lambda: defaultdict(list)))

    iterated = {
        year: {inner_key: dict(group)} if inner_key else dict(group)
        for year, group in grouped.items()
    }

    return dict(sorted(iterated.items())) if sort_result else iterated


# --- Group nodes by last date ---


def _get_last_date(datestrs: list[str]) -> Optional[str]:
    """
    Reduce a datestrs down to a single datestr by selecting the last one.

    Parameters
    ----------
    datestrs : list
        A list of datestrings, e.g. the value of a node's `dates` field.

    Returns
    -------
    str | None
        Returns the latest datestr or `None` if no valid datestr in list.

    """
    return sorted(datestrs)[-1] if len(datestrs) > 0 else None


def group_nodes_by_last_date(nodes: list) -> dict[str, list[dict]]:
    """
    Group a list of nodes by the last date of their `dates` field. Nodes with no `dates` field will be sorted into
    the `no-dates` group.

    Parameters
    ----------
    nodes : list[dict]
        A list of HESTIA format nodes.

    Return
    ------
    dict
        A dictionary of nodes grouped by latest date, in the format `{date: list[node]}`.
    """
    DEFAULT_KEY = 'no-dates'

    def group_by(group: dict, node: dict):
        dates = node.get('dates', [])
        key = _get_last_date(dates) or DEFAULT_KEY
        return group | {key: group.get(key, []) + [node]}

    return reduce(group_by, nodes, {})


def get_inputs_from_properties(input: dict, term_types: Union[TermTermType, List[TermTermType]]):
    """
    Compute a list of inputs from the input properties, in the `key:value` form.

    Parameters
    ----------
    input : dict
        The Input.
    term_types : TermTermType | List[TermTermType]
        List of `termType` valid for the properties `key`.

    Return
    ------
    dict
        A dictionary of nodes grouped by latest date, in the format `{date: list[node]}`.
    """
    term = input.get('term', {})
    input_value = list_sum(input.get('value', []))
    properties = (
        input.get('properties') or
        term.get('defaultProperties') or
        download_term(term).get('defaultProperties')
    )
    inputs = non_empty_list([
        {
            'term': p.get('key'),
            'value': [(p.get('value') / 100) * (p.get('share', 100) / 100) * input_value],
            # for grouping
            'parent': term
        } for p in (properties or []) if all([p.get('key'), p.get('value')])
    ]) if input_value > 0 else []
    return filter_list_term_type(inputs, term_types)


def _has_unique_key(nodes: list, key: str): return len(set([n.get(key) for n in nodes])) == 1


def _same_dates(nodes: list): return all([_has_unique_key(nodes, 'startDate'), _has_unique_key(nodes, 'endDate')])


def _should_group_node(node: dict): return node.get('startDate') and node.get('endDate')


def _parse_date(node: dict, key: str):
    return safe_parse_date(full_date_str(node.get(key), is_end=key == 'endDate'))


def _group_nodes_by_consecutive_dates(nodes: list):
    """Groups dictionaries in a list based on consecutive start and end dates within a 1-day tolerance.

    Args:
        dicts: A list of dictionaries containing 'startDate' and 'endDate' keys.

    Returns:
        A list of lists, where each inner list contains dictionaries with consecutive start and end dates.
    """
    groups = []
    group = []

    # make sure the nodes are sorted by dates to group by consecutive dates
    for n in sorted(nodes, key=lambda d: (_parse_date(d, 'startDate'), _parse_date(d, 'endDate'))):
        if not group or (
            _should_group_node(n) and
            _parse_date(n, 'startDate') - _parse_date(group[-1], 'endDate') <= timedelta(days=1)
        ):
            group.append(n)
        else:
            groups.append(group)
            group = [n]

    if group:
        groups.append(group)

    # if all nodes have a single startDate and endDate, then they are all the same
    return [nodes] if _same_dates(nodes) else groups


def _sum_nodes_value(nodes: list):
    values = flatten([n.get('value', []) for n in nodes])
    is_boolean = all([isinstance(v, bool) for v in values])
    return values[0] if is_boolean else [list_sum(values)] if isinstance(nodes[0]['value'], list) else list_sum(values)


def _node_from_group(nodes: list):
    # `nodes` contain list with consecutive dates
    return nodes[0] if len(nodes) == 1 else (
        # if all nodes have the same dates, sum up the values
        nodes[0] | (
            {
                'value': _sum_nodes_value(nodes)
            } if _same_dates(nodes) else {
                'startDate': min(n.get('startDate') for n in nodes),
                'endDate': max(n.get('endDate') for n in nodes)
            }
        )
    )


def _condense_nodes(nodes: list):
    # `nodes` contain list with same `term.@id` and `value`
    grouped_nodes = _group_nodes_by_consecutive_dates(nodes)
    return flatten(map(_node_from_group, grouped_nodes))


def _group_nodes_by_value_and_properties(nodes: list) -> dict:
    def _group_node(group: dict, node: dict):
        value = node.get('value', [])
        value = '-'.join(map(str, value if isinstance(value, list) else [value]))
        properties = '_'.join(non_empty_list([
            ';'.join(non_empty_list([
                p.get('term', {}).get('@id'),
                f"{p.get('value')}"
            ])) for p in node.get('properties', [])
        ]))
        group_key = '-'.join(non_empty_list([
            node.get('term', {}).get('@id', ''),
            value,
            properties
        ]))
        group[group_key] = group.get(group_key, []) + [node]
        return group

    return reduce(_group_node, nodes, {})


def _group_nodes_by_dates(nodes: list) -> dict:
    def _group_node(group: dict, node: dict):
        group_key = '-'.join(non_empty_list([
            node.get('term', {}).get('@id', ''),
            node.get('startDate'),
            node.get('endDate'),
        ]))
        group[group_key] = group.get(group_key, []) + [node]
        return group

    return reduce(_group_node, nodes, {})


def _average_properties(properties: list):
    # group properties by term
    grouped_properties = group_by_term(properties)
    return [
        props[0] | {
            'value': list_average(non_empty_list([p.get('value') for p in props]), default=props[0].get('value'))
        }
        for props in grouped_properties.values()
    ]


def _merge_same_dates(nodes: list):
    # group by term, startDate and endDate
    grouped_nodes = _group_nodes_by_dates(nodes)

    def merge_nodes(nodes: list):
        properties = flatten([n.get('properties', []) for n in nodes])
        return nodes[0] | (
            {
                'value': _sum_nodes_value(nodes)
            } | ({
                'properties': _average_properties(properties)
            } if properties else {})
        ) if len(nodes) > 1 else nodes[0]

    return list(map(merge_nodes, grouped_nodes.values()))


def condense_nodes(nodes: list) -> list:
    # merge nodes with the same term and dates as they need to be unique
    values = _merge_same_dates(nodes)
    grouped_nodes = _group_nodes_by_value_and_properties(values)
    return flatten(map(_condense_nodes, grouped_nodes.values()))


def _node_date(node: dict): return parser.isoparse(node.get('endDate', OLDEST_DATE))


def _distance(node: dict, date): return abs((_node_date(node) - date).days)


def _most_recent_nodes(nodes: list, date: str) -> list:
    closest_date = parser.isoparse(date)
    min_distance = min([_distance(m, closest_date) for m in nodes])
    return list(filter(lambda m: _distance(m, closest_date) == min_distance, nodes))


def _shallowest_node(nodes: list) -> dict:
    min_depth = min([m.get('depthUpper', MAX_DEPTH) for m in nodes])
    return next((m for m in nodes if m.get('depthUpper', MAX_DEPTH) == min_depth), {})


def most_relevant_blank_node_by_type(nodes: List[dict],
                                     term_type: Union[TermTermType, str, List[TermTermType], List[str]], date: str):
    """
    Given a list of cycle specific dated entries like
    a list of measurements terms or a list of management terms,
    find the entry closest to a given date
    Parameters
    ----------
    nodes: List[dict]
        should contain a 'endDate' field otherwise defaults to OLDEST_DATE
    term_type : TermTermType or List[TermTermType]
        The `termType` of the `Term`, or a list of `termType`. Example: `TermTermType.CROP`
    date: str
        An ISO-8601 datetime compatible string

    Returns
    -------

    """
    filtered_nodes = filter_list_term_type(nodes, term_type)

    return {} if len(filtered_nodes) == 0 \
        else _shallowest_node(_most_recent_nodes(filtered_nodes, date)) \
        if date and len(filtered_nodes) > 1 else filtered_nodes[0]


def most_relevant_blank_node_by_id(nodes: list, term_id: str, date: str):
    """
        Given a list of nodes with term_id like
        a list of measurements terms or a list of management terms,
        find the entry closest to a given date
        Parameters
        ----------
        nodes: List[dict]
            should contain a 'endDate' field otherwise defaults to OLDEST_DATE
        term_id : str
            the term "@id" of the node we want to match to
        date: str
            An ISO-8601 datetime compatible string

        Returns
        -------

        """
    filtered_nodes = [m for m in nodes if m.get('term', {}).get('@id') == term_id]
    return {} if len(filtered_nodes) == 0 \
        else _shallowest_node(_most_recent_nodes(filtered_nodes, date)) \
        if date and len(filtered_nodes) > 1 else filtered_nodes[0]


PROPERTY_UNITS_CONVERSIONS = {
    Units.KG.value: {
        Units.MJ.value: [
            'energyContentLowerHeatingValue',  # "kg" to "mj"
        ]
    },
    Units.M3.value: {
        Units.MJ.value: [
            'density',  # "m3" to "kg"
            'energyContentLowerHeatingValue',  # "kg" to "mj"
        ]
    }
}


def _convert_via_property(node: dict, node_value: Union[int, float], property_field: str) -> Optional[float]:
    """
    Converts a node_value number from one unit to another using a property_field  associated
    with a term inside term node such as "density" or 'energyContentHigherHeatingValue' or listed
    in https://www.hestia.earth/glossary?page=1&termType=property

    Will return none if the property_field is not found

    Parameters
    ----------
    node: dict
        Blank node containing a term
    node_value: int | float
        Value to be converted as float or int
    property_field: str
        E.g., "density"

    Returns
    -------
        Float or None
    """
    node_property_value = get_node_property_value(
        model=None, node=node, prop_id=property_field, default=0, handle_percents=False
    )
    return node_value * node_property_value if node_value is not None and bool(node_property_value) else None


def convert_unit(node, dest_unit: Units, node_value: Union[int, float] = None) -> Optional[Union[int, float]]:
    """
    Convert a number `value` inside a node or a optional `node_value` belonging to a term `node`, to unit `dest_unit`
    using the ATOMIC_WEIGHT_CONVERSIONS map or failing that, the PROPERTY_UNITS_CONVERSIONS map and lookups
    """
    src_unit = node.get("units") or node.get('term', {}).get('units', "")

    node_value = _node_value(node) if node_value is None else node_value

    return node_value if src_unit == dest_unit.value else (
        node_value * get_atomic_conversion(src_unit, dest_unit)
        if get_atomic_conversion(src_unit, dest_unit, default_value=None) is not None
        else convert_unit_properties(node_value, node, dest_unit)
    ) if node_value else None


def convert_unit_properties(node_value: Union[int, float], node: dict, dest_unit: Units) -> Optional[Union[int, float]]:
    """
    Convert a number `node_value` belonging to a term `node`, to unit `to_units` by chaining multiple unit conversions
    together.
    Uses terms properties for the conversion.
    Returns None if no conversion possible.
    """
    src_unit = node.get("units") or node.get('term', {}).get('units', "")
    conversions = PROPERTY_UNITS_CONVERSIONS.get(src_unit, {}).get(dest_unit.value, [])
    return reduce(
        lambda value, conversion_property_field: _convert_via_property(node, value, conversion_property_field),
        conversions, node_value
    ) if conversions else None


def validate_start_date_end_date(node: dict) -> bool:
    """Return `True` if `node.startDate` is before `node.endDate`, `False` if otherwise."""
    start_date = _gapfill_datestr(node.get("startDate", OLDEST_DATE))
    end_date = _gapfill_datestr(node.get("endDate", OLDEST_DATE), DatestrGapfillMode.END)

    return safe_parse_date(start_date) < safe_parse_date(end_date)
