import os
from functools import reduce
from hestia_earth.schema import NodeType
from hestia_earth.utils.tools import current_time_ms, flatten
from hestia_earth.earth_engine import init_gee

from .log import logger
from .utils import CACHE_KEY
from .utils.site import years_from_cycles
from .utils.source import CACHE_SOURCES_KEY, find_sources
from .cache_sites import run as cache_sites

CACHE_RELATED_KEY = 'related'
CACHE_NESTED_KEY = 'nested'

_CACHE_BATCH_SIZE = int(os.getenv('CACHE_SITES_BATCH_SIZE', '5000'))
_ENABLE_CACHE_YEARS = os.getenv('ENABLE_CACHE_YEARS', 'true') == 'true'
_ENABLE_CACHE_RELATED_NODES = os.getenv('ENABLE_CACHE_RELATED_NODES', 'true') == 'true'
_CACHE_NODE_TYPES = [
    NodeType.SITE.value,
    NodeType.CYCLE.value,
    NodeType.IMPACTASSESSMENT.value
]


def _pop_items(values: list, nb_items: int):
    if len(values) < nb_items:
        removed_items = values[:]  # Get a copy of the entire array
        values.clear()  # Remove all items from the original array
    else:
        removed_items = values[:nb_items]  # Get the first N items
        del values[:nb_items]  # Remove the first N items from the original array

    return removed_items


def _filter_by_type(nodes: list, type: str): return [n for n in nodes if n.get('@type', n.get('type')) == type]


def _node_key(node: dict): return '/'.join([node.get('type', node.get('@type')), node.get('id', node.get('@id'))])


def _years_from_cycles(nodes: dict): return years_from_cycles(_filter_by_type(nodes, NodeType.CYCLE.value))


def _linked_node(data: dict): return {'type': data.get('type'), 'id': data.get('id')}


def _find_nested_nodes(data) -> list[dict]:
    if isinstance(data, dict):
        if data.get('type') in _CACHE_NODE_TYPES and data.get('id'):
            return [_linked_node(data)]
        return flatten(_find_nested_nodes(list(data.values())))
    if isinstance(data, list):
        return flatten(map(_find_nested_nodes, data))
    return []


def _nested_nodes(node_keys: list[str]):
    def exec(group: dict, node: dict):
        nested_nodes = _find_nested_nodes(list(node.values()))

        for nested_node in nested_nodes:
            group_id = _node_key(nested_node)
            group[group_id] = group.get(group_id, {})
            group[group_id][CACHE_RELATED_KEY] = group.get(group_id, {}).get(CACHE_RELATED_KEY, []) + [
                _linked_node(node)
            ]

            # cache nodes that current node refers (nesting)
            if group_id in node_keys:
                group_id = _node_key(node)
                group[group_id] = group.get(group_id, {})
                group[group_id][CACHE_NESTED_KEY] = group.get(group_id, {}).get(CACHE_NESTED_KEY, []) + [
                    _linked_node(nested_node)
                ]

        return group
    return exec


def _cache_related_nodes(nodes: list):
    # only cache nodes included in the file
    nodes_keys = list(map(_node_key, nodes))
    # for each node, compile list of nested nodes
    nested_nodes_mapping = reduce(_nested_nodes(nodes_keys), nodes, {})

    def cache_related_node(node: dict):
        nodes_mapping = nested_nodes_mapping.get(_node_key(node), {})
        related_nodes = nodes_mapping.get(CACHE_RELATED_KEY) or []
        nested_nodes = nodes_mapping.get(CACHE_NESTED_KEY) or []
        # save in cache
        cached_data = node.get(CACHE_KEY, {}) | {
            CACHE_RELATED_KEY: related_nodes,
            CACHE_NESTED_KEY: nested_nodes
        }
        return node | {CACHE_KEY: cached_data}

    return list(map(cache_related_node, nodes))


def _cache_sources(nodes: list):
    sources = find_sources()
    return [
        n | ({
            CACHE_KEY: n.get(CACHE_KEY, {}) | {CACHE_SOURCES_KEY: sources}
        } if n.get('type', n.get('@type')) in _CACHE_NODE_TYPES else {})
        for n in nodes
    ]


def _safe_cache_sites(sites: list, years: list):
    try:
        return cache_sites(sites, years)
    except Exception as e:
        logger.error(f"An error occured while caching nodes on EE: {str(e)}")
        if 'exceeded' in str(e):
            logger.debug('Fallback to caching sites one by one')
            # run one by one in case the batching does not work
            return flatten([cache_sites([site], years) for site in sites])
        else:
            raise e


def _cache_sites(nodes: list, batch_size: int = _CACHE_BATCH_SIZE):
    start = current_time_ms()

    # build list of nodes by key to update as sites are processed
    nodes_mapping = {_node_key(n): n for n in nodes}

    years = _years_from_cycles(nodes) if _ENABLE_CACHE_YEARS else []
    sites = _filter_by_type(nodes, 'Site')

    while len(sites) > 0:
        batch_values = _pop_items(sites, batch_size)
        logger.info(f"Processing {len(batch_values)} sites / {len(sites)} remaining.")
        results = _safe_cache_sites(batch_values, years)
        for result in results:
            nodes_mapping[_node_key(result)] = result

    logger.info(f"Done caching sites in {current_time_ms() - start} ms")

    # replace original sites with new cached sites
    return list(nodes_mapping.values())


def run(nodes: list):
    init_gee()

    # cache sites data
    cached_nodes = _cache_sites(nodes)

    # cache related nodes
    cached_nodes = _cache_related_nodes(cached_nodes) if _ENABLE_CACHE_RELATED_NODES else cached_nodes

    # cache sources
    return _cache_sources(cached_nodes)
