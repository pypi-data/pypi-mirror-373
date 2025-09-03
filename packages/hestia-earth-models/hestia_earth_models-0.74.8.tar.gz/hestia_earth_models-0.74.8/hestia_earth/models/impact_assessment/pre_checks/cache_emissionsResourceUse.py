from hestia_earth.utils.blank_node import group_by_keys, get_node_value, ArrayTreatment
from hestia_earth.utils.tools import non_empty_list

_GROUP_KEYS = ['term', 'methodModel', 'inputs', 'operation', 'country', 'region']


def _grouped_blank_node(blank_nodes: list):
    blank_node = {
        key: blank_nodes[0].get(key) for key in _GROUP_KEYS if blank_nodes[0].get(key)
    } | {
        'value': non_empty_list([v.get('value') for v in blank_nodes])
    }
    value = get_node_value(blank_node, default_array_treatment=ArrayTreatment.SUM)
    return blank_node | {'value': value}


def run(impact: dict):
    blank_nodes = impact.get('emissionsResourceUse', [])
    grouped_blank_nodes = group_by_keys(blank_nodes, _GROUP_KEYS)
    grouped_blank_nodes = [_grouped_blank_node(value) for value in grouped_blank_nodes.values()]
    return grouped_blank_nodes
