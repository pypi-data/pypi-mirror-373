from functools import lru_cache
from typing import Optional, List
from hestia_earth.utils.lookup import (
    download_lookup,
    get_table_value,
    column_name,
    extract_grouped_data,
    _get_single_table_value
)
from hestia_earth.utils.tools import list_sum, safe_parse_float, non_empty_list

from ..log import debugValues, log_as_table, debugMissingLookup


def _node_value(node):
    value = node.get('value')
    return list_sum(value, default=None) if isinstance(value, list) else value


def _log_value_coeff(log_node: dict, value: float, coefficient: float, **log_args):
    if value is not None and coefficient:
        debugValues(log_node, value=value, coefficient=coefficient, **log_args)


def _factor_value(
    log_node: dict,
    model: str,
    term_id: str,
    lookup_name: str,
    lookup_col: str,
    group_key: Optional[str] = None,
    default_world_value: Optional[bool] = False
):
    @lru_cache()
    def get_coefficient(node_term_id: str, grouped_data_key: str):
        coefficient = get_region_lookup_value(
            lookup_name=lookup_name,
            term_id=node_term_id,
            column=lookup_col,
            fallback_world=default_world_value,
            model=model, term=term_id
        )
        # value is either a number or matching between a model and a value (restrict value to specific model only)
        return safe_parse_float(
            extract_grouped_data(coefficient, grouped_data_key),
            default=None
        ) if ':' in str(coefficient) else safe_parse_float(coefficient, default=None)

    def get_value(blank_node: dict):
        node_term_id = blank_node.get('term', {}).get('@id')
        grouped_data_key = group_key or blank_node.get('methodModel', {}).get('@id')
        value = _node_value(blank_node)
        coefficient = get_coefficient(node_term_id, grouped_data_key)
        if model:
            _log_value_coeff(log_node=log_node, value=value, coefficient=coefficient,
                             model=model,
                             term=term_id,
                             node=node_term_id,
                             operation=blank_node.get('operation', {}).get('@id'))
        return {'id': node_term_id, 'value': value, 'coefficient': coefficient}
    return get_value


def region_factor_value(
    log_node: dict,
    model: str,
    term_id: str,
    lookup_name: str,
    lookup_term_id: str,
    group_key: Optional[str] = None,
    default_world_value: Optional[bool] = False
):
    @lru_cache()
    def get_coefficient(node_term_id: str, region_term_id: str):
        coefficient = get_region_lookup_value(
            lookup_name=lookup_name,
            term_id=region_term_id,
            column=node_term_id,
            fallback_world=default_world_value,
            model=model, term=term_id
        )
        return safe_parse_float(
            extract_grouped_data(coefficient, group_key) if group_key else coefficient,
            default=None
        )

    def get_value(blank_node: dict):
        node_term_id = blank_node.get('term', {}).get('@id')
        value = _node_value(blank_node)
        # when getting data for a `region`, we can try to get the `region` on the node first, in case it is set
        region_term_id = (
            (blank_node.get('region') or blank_node.get('country') or {'@id': lookup_term_id}).get('@id')
        ) if lookup_term_id.startswith('GADM-') else lookup_term_id
        coefficient = get_coefficient(node_term_id, region_term_id)
        _log_value_coeff(log_node=log_node, value=value, coefficient=coefficient,
                         model=model,
                         term=term_id,
                         node=node_term_id,
                         operation=blank_node.get('operation', {}).get('@id'))
        return {'id': node_term_id, 'region-id': region_term_id, 'value': value, 'coefficient': coefficient}
    return get_value


def aware_factor_value(
    log_node: dict,
    model: str,
    term_id: str,
    lookup_name: str,
    aware_id: str,
    group_key: Optional[str] = None,
    default_world_value: Optional[bool] = False
):
    lookup = download_lookup(lookup_name, False)  # avoid saving in memory as there could be many different files used
    lookup_col = column_name('awareWaterBasinId')

    @lru_cache()
    def get_coefficient(node_term_id: str):
        coefficient = _get_single_table_value(lookup, lookup_col, int(aware_id), column_name(node_term_id))
        return safe_parse_float(
            extract_grouped_data(coefficient, group_key),
            default=None
        ) if group_key else coefficient

    def get_value(blank_node: dict):
        node_term_id = blank_node.get('term', {}).get('@id')
        value = _node_value(blank_node)

        try:
            coefficient = get_coefficient(node_term_id)
            _log_value_coeff(log_node=log_node, value=value, coefficient=coefficient,
                             model=model,
                             term=term_id,
                             node=node_term_id)
        except Exception:  # factor does not exist
            coefficient = None

        return {'id': node_term_id, 'value': value, 'coefficient': coefficient}
    return get_value


def all_factor_value(
    log_model: str,
    log_term_id: str,
    log_node: dict,
    lookup_name: str,
    lookup_col: str,
    blank_nodes: List[dict],
    group_key: Optional[str] = None,
    default_no_values=0,
    factor_value_func=_factor_value,
    default_world_value: bool = False
):
    values = list(map(
        factor_value_func(log_node, log_model, log_term_id, lookup_name, lookup_col, group_key, default_world_value),
        blank_nodes
    ))

    has_values = len(values) > 0
    missing_values = set([
        '_'.join(non_empty_list([v.get('id'), v.get('region-id')]))
        for v in values
        if v.get('value') and v.get('coefficient') is None
    ])
    all_with_factors = not missing_values

    for missing_value in missing_values:
        debug_values = missing_value.split('_')
        debugMissingLookup(
            lookup_name=lookup_name,
            row='termid',
            row_value=debug_values[1] if len(debug_values) == 2 else debug_values[0],
            col=debug_values[0] if len(debug_values) == 2 else lookup_col,
            value=None,
            model=log_model,
            term=log_term_id
        )

    debugValues(log_node, model=log_model, term=log_term_id,
                all_with_factors=all_with_factors,
                missing_lookup_factor=log_as_table([
                    {
                        'id': v.split('_')[0]
                    } | ({
                        'region-id': v.split('_')[1]
                    } if len(v.split('_')) == 2 else {})
                    for v in missing_values
                ]),
                has_values=has_values,
                values_used=log_as_table([v for v in values if v.get('coefficient')]))

    values = [float((v.get('value') or 0) * (v.get('coefficient') or 0)) for v in values]

    # fail if some factors are missing
    return None if not all_with_factors else (list_sum(values) if has_values else default_no_values)


def get_region_lookup(lookup_name: str, term_id: str):
    # for performance, try to load the region specific lookup if exists
    return (
        download_lookup(lookup_name.replace('region-', f"{term_id}-"), build_index=True)
        if lookup_name and lookup_name.startswith('region-') else None
    ) or download_lookup(lookup_name, build_index=True)


@lru_cache()
def get_region_lookup_value(lookup_name: str, term_id: str, column: str, fallback_world: bool = False, **log_args):
    # for performance, try to load the region specific lookup if exists
    lookup = get_region_lookup(lookup_name, term_id)
    value = get_table_value(lookup, 'termid', term_id, column_name(column))
    if value is None and fallback_world:
        return get_region_lookup_value(lookup_name, 'region-world', column, **log_args)
    debugMissingLookup(lookup_name, 'termid', term_id, column, value, **log_args)
    return value
