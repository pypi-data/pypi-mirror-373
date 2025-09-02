from hestia_earth.utils.tools import list_average

from hestia_earth.models.log import logShouldRun
from . import MODEL


def _should_run_property_by_min_max(property: dict):
    return all([
        property.get('min') is not None,
        property.get('max') is not None
    ])


def _run_property(cycle: dict, property: dict, **log_args):
    term_id = property.get('term', {}).get('@id')

    should_run = _should_run_property_by_min_max(property)
    logShouldRun(cycle, MODEL, term_id, should_run, key='value', **log_args)

    return property | ({
        'value': list_average([property.get('min'), property.get('max')])
    } if should_run else {})


def _run_properties(cycle: dict, blank_node: dict, **log_args):
    properties = blank_node.get('properties', [])
    return blank_node | ({
        'properties': [_run_property(cycle, p, **log_args) for p in properties]
    } if properties else {})


def should_run_properties_value(blank_node: dict):
    return any(map(_should_run_property_by_min_max, blank_node.get('properties', [])))


def average_blank_node_properties_value(cycle: dict, blank_nodes: list, **log_args):
    return [_run_properties(cycle, v, **log_args) for v in blank_nodes]
