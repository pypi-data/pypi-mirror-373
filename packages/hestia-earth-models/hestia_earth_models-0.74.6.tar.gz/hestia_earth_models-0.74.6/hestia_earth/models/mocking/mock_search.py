import json
from functools import cache

from hestia_earth.models.utils import term

_original_search_func = term.search
_original_find_node_func = term.find_node


def _load_results(filepath: str) -> dict:
    with open(filepath) as f:
        return json.load(f)


_load_results_cached = cache(_load_results)


def _find_search_result(filepath: str, query: dict, keep_in_memory: bool):
    _load_results_func = _load_results_cached if keep_in_memory else _load_results
    search_results = _load_results_func(filepath)
    res = next((n for n in search_results if n['query'] == query), None)
    return None if res is None else res.get('results', [])


def _mocked_search(filepath: str, keep_in_memory: bool):
    def mock(query: dict, **kwargs):
        result = _find_search_result(filepath, query, keep_in_memory)
        return _original_search_func(query, **kwargs) if result is None else result
    return mock


def _mocked_find_node(filepath: str, keep_in_memory: bool):
    def mock(node_type: str, query: dict, **kwargs):
        result = _find_search_result(filepath, query, keep_in_memory)
        return _original_find_node_func(node_type, query, **kwargs) if result is None else result
    return mock


def mock(filepath: str, keep_in_memory: bool):
    term.search = _mocked_search(filepath, keep_in_memory)
    term.find_node = _mocked_find_node(filepath, keep_in_memory)


def unmock():
    term.search = _original_search_func
    term.find_node = _original_find_node_func
