from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value
from hestia_earth.utils.tools import safe_parse_float, list_sum

from hestia_earth.models.log import debugValues, debugMissingLookup, log_as_table
from . import _filter_list_term_unit
from .constant import Units
from .term import get_lookup_value


def get_lookup_factor(practices: list, lookup_col: str):
    practices = filter_list_term_type(practices, TermTermType.EXCRETAMANAGEMENT)
    practice = practices[0].get('term', {}) if len(practices) > 0 else None
    return get_lookup_value(practice, lookup_col) if practice else None


def _get_nh3_factor(lookup_name: str, term_id: str, input: dict, **log_args):
    input_term_id = input.get('term', {}).get('@id')
    value = get_table_value(download_lookup(lookup_name), 'termid', term_id, column_name(input_term_id))
    debugMissingLookup(lookup_name, 'termid', term_id, input_term_id, value, **log_args)
    return safe_parse_float(value, default=None)


def get_excreta_inputs_with_factor(cycle: dict, lookup_name: str, excreta_conversion_func, **log_args):
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.EXCRETAMANAGEMENT)
    practice_id = practices[0].get('term', {}).get('@id') if len(practices) > 0 else None

    # total of excreta including the factor
    excreta_inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.EXCRETA)
    excreta_inputs = _filter_list_term_unit(excreta_inputs, Units.KG_N)
    excreta_values = [
        (
            i.get('term', {}).get('@id'),
            excreta_conversion_func([i]),
            _get_nh3_factor(lookup_name, practice_id, i, **log_args)
        ) for i in excreta_inputs
    ]
    excreta_logs = log_as_table([
        {'id': id, 'value': v, 'EF': ef} for id, v, ef in excreta_values
    ])
    has_excreta_EF_inputs = len(excreta_values) > 0
    debugValues(cycle, **log_args,
                practice_id=practice_id,
                has_excreta_EF_inputs=has_excreta_EF_inputs,
                excreta=excreta_logs)
    return list_sum([v * f for id, v, f in excreta_values if v is not None and f is not None], 0)
