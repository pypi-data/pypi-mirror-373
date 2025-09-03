from inspect import getmembers, isfunction
from hestia_earth.utils.tools import flatten

from hestia_earth.models.utils import term

_IGNORE_FUNC = ['get_lookup_value', 'get_table_value']
_original_search_func = term.search
_original_find_node_func = term.find_node


def _map_results(results):
    # returning the whole term
    return [results] if isinstance(results, dict) else (
        {'@type': 'Term', '@id': results} if isinstance(results, str) else
        flatten(map(_map_results, results)) if isinstance(results, list) else
        None
    )


def _create_search_result(data: tuple):
    search_query = {}

    def new_search(query: dict, *_a, **_b):
        nonlocal search_query
        search_query = query
        return _original_search_func(query, *_a, **_b)

    term.search = new_search

    def new_find_node(_n, query: dict, *_a, **_b):
        nonlocal search_query
        search_query = query
        return _original_find_node_func(_n, query, *_a, **_b)

    term.find_node = new_find_node

    function_name, func = data
    res = func()
    return {'name': function_name, 'query': search_query, 'results': _map_results(res)}


def create_search_results():
    funcs = list(filter(lambda v: v[0].startswith('get_') and not v[0] in _IGNORE_FUNC, getmembers(term, isfunction)))
    return list(map(_create_search_result, funcs))
