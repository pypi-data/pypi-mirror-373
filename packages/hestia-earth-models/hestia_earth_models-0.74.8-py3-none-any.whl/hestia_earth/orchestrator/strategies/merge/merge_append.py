from functools import reduce
from hestia_earth.orchestrator.utils import _non_empty_list, update_node_version

from hestia_earth.orchestrator.log import logger


def _merge_node(dest: dict, version: str):
    term_id = dest.get('term', {}).get('@id', dest.get('@id'))
    logger.debug('append %s with value: %s', term_id, dest.get('value'))
    return [update_node_version(version, dest)]


_MERGE_BY_TYPE = {
    'dict': _merge_node,
    'list': lambda dest, *args: dest
}


def _merge_el(version: str):
    def merge(source: list, dest: dict):
        ntype = type(dest).__name__
        return source + _MERGE_BY_TYPE.get(ntype, lambda *args: [dest])(dest, version)
    return merge


def merge(source: list, dest, version: str, *args):
    source = source if source is not None else []
    nodes = _non_empty_list(dest if isinstance(dest, list) else [dest])
    return reduce(_merge_el(version), nodes, source)
