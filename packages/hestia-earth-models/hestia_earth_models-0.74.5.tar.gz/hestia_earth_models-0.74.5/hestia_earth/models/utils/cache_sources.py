from . import CACHE_KEY, cached_value
from .source import CACHE_SOURCES_KEY, find_sources


def _run(): return {CACHE_SOURCES_KEY: find_sources()}


def _has_value(node: dict): return bool(cached_value(node, CACHE_SOURCES_KEY))


def cache_sources(node: dict):
    return {
        **node,
        CACHE_KEY: cached_value(node) | _run()
    } if not _has_value(node) else node
