from os.path import dirname, abspath
from collections.abc import Generator, Iterable
from itertools import tee
from decimal import Decimal
from statistics import mean
import sys
import datetime
from functools import reduce
import operator
from pydash.objects import get
from typing import Union, List, Callable
from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.tools import flatten, non_empty_list, safe_parse_date
from hestia_earth.utils.date import is_in_days, is_in_months

from .constant import Units

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)
CACHE_KEY = '_cache'


def cached_value(node: dict, key: str = None, default=None):
    cache = node.get(CACHE_KEY, {})
    return cache.get(key, default) if all([
        key,
        cache is not None
    ]) else cache


def group_by(values: list, keys: list):
    def _group_by(group: dict, value: dict):
        group_key = ';'.join(non_empty_list([get(value, key) for key in keys]))
        group[group_key] = group.get(group_key, []) + [value]
        return group
    return reduce(_group_by, values, {})


def _term_id(term): return term.get('@id') if isinstance(term, dict) else term


def _omit(values: dict, keys: list) -> dict: return {k: v for k, v in values.items() if k not in keys}


def _include(value: dict, keys: list) -> dict: return {k: v for k, v in value.items() if k in keys}


def unique_values(values: list, key='@id'): return list({v[key]: v for v in values}.values())


def _run_in_serie(data: dict, models: list): return reduce(lambda prev, model: model(prev), models, data)


def _load_calculated_node(node, type: SchemaType, data_state='recalculated'):
    # return original value if recalculated is not available
    return download_hestia(node.get('@id'), type, data_state=data_state) or download_hestia(node.get('@id'), type)


def _unit_str(unit) -> str: return unit if isinstance(unit, str) else unit.value


def _filter_list_term_unit(values: list, unit: Union[str, List[str]]):
    units = unit if isinstance(unit, list) else [unit]
    units = list(map(_unit_str, units))
    return list(filter(lambda i: i.get('term', {}).get('units') in units, values))


def is_from_model(node: dict) -> bool:
    """
    Check if the Blank Node came from one of the HESTIA Models.

    Parameters
    ----------
    node : dict
        The Blank Node containing `added` and `updated`.

    Returns
    -------
    bool
        `True` if the value came from a model, `False` otherwise.
    """
    return 'value' in node.get('added', []) or 'value' in node.get('updated', [])


def sum_values(values: list):
    """
    Sum up the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return sum(filtered_values) if len(filtered_values) > 0 else None


def multiply_values(values: list):
    """
    Multiply the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return reduce(operator.mul, filtered_values, 1) if len(filtered_values) > 1 else None


def _numeric_weighted_average(values: list):
    total_weight = sum(Decimal(str(weight)) for _v, weight in values) if values else Decimal(0)
    weighted_values = [Decimal(str(value)) * Decimal(str(weight)) for value, weight in values]
    average = sum(weighted_values) / (total_weight if total_weight else 1) if weighted_values else None
    return None if average is None else float(average)


def _bool_weighted_average(values: list):
    return mean(map(int, values)) >= 0.5


def weighted_average(weighted_values: list):
    values = [v for v, _w in weighted_values]
    all_boolean = all([isinstance(v, bool) for v in values])
    return _bool_weighted_average(values) if all_boolean else _numeric_weighted_average(weighted_values)


def term_id_prefix(term_id: str): return term_id.split('Kg')[0]


def get_kg_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgMass"


def get_kg_N_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgN"


def get_kg_P2O5_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgP2O5"


def get_kg_K2O_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgK2O"


def get_kg_VS_term_id(term_id: str): return f"{term_id_prefix(term_id)}KgVs"


def get_kg_term_units(term_id: str, units: str):
    return {
        Units.KG.value: get_kg_term_id,
        Units.KG_N.value: get_kg_N_term_id,
        Units.KG_P2O5.value: get_kg_P2O5_term_id,
        Units.KG_K2O.value: get_kg_K2O_term_id,
        Units.KG_VS.value: get_kg_VS_term_id
    }.get(units, lambda x: None)(term_id)


def first_day_of_month(year: int, month: int):
    return datetime.date(int(year), int(month), 1)


def last_day_of_month(year: int, month: int):
    # handle special case month 12
    return datetime.date(int(year), 12, 31) if month == 12 else (
        datetime.date(int(year) + int(int(month) / 12), (int(month) % 12) + 1, 1) - datetime.timedelta(days=1)
    )


def current_date(): return datetime.datetime.now().date().strftime('%Y-%m-%d')


def current_year(): return int(current_date()[:4])


def max_date(date_str: str):
    """
    If the date is after today, returns today. Otherwise returns the date.
    """
    date = safe_parse_date(date_str).date()
    max_date = datetime.datetime.now().date()
    return current_date() if date > max_date else date_str


def flatten_args(args) -> list:
    """
    Flatten the input args into a single list.
    """
    return non_empty_list(flatten([list(arg) if is_iterable(arg) else [arg] for arg in args]))


def is_iterable(arg) -> bool:
    """
    Return `True` if the input arg is an instance of an `Iterable` (excluding `str` and `bytes`) or a `Generator`, else
    return `False`.
    """
    return isinstance(arg, (Iterable, Generator)) and not isinstance(arg, (str, bytes))


def pairwise(iterable):
    """
    from https://docs.python.org/3.9/library/itertools.html#itertools-recipes
    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def full_date_str(date_str: str, is_end: bool = False):
    """
    Return the date in format YYY-MM-dd, by setting the month and day if they are not provided.
    """
    return date_str if is_in_days(date_str) else (
        f"{date_str}-{14 if is_end else 15}" if is_in_months(date_str)
        else f"{date_str}-{'12-31' if is_end else '01-01'}"
    )


def days_to_years(days): return days / 365


def hectar_to_square_meter(value): return value * 10000


def square_meter_to_hectare(value): return value / 10000


def split_on_condition(iterable: Iterable, condition: Callable):
    """
    Split an iterable into two iterables of the same type based on whether or not each item satisfies a condition.
    """
    def construct(iterator: Generator) -> Iterable:
        return ''.join(iterable) if isinstance(iterable, str) else type(iterable)(iterator)

    cond_true, cond_false = tee((condition(item), item) for item in iterable)
    return construct(i for p, i in cond_true if p), construct(i for p, i in cond_false if not p)
