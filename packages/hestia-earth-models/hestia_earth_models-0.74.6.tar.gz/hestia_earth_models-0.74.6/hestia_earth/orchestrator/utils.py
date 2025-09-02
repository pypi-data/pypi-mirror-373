from typing import Union
import re
from statistics import mean
from functools import reduce

EXCLUDED_VERSION_KEYS = [
    '@type'
]
_memory = {}


def wrap_index(key: str, sub_key: str, func):
    global _memory  # noqa: F824
    memory_data = _memory.get(key, {})
    data = (memory_data.get('data') if memory_data.get('sub_key') == sub_key else None) or func()
    _memory[key] = {
        'sub_key': sub_key,
        'data': data
    }
    return data


def update_index(key: str, sub_key: str, data):
    global _memory  # noqa: F824
    _memory[key] = {
        'sub_key': sub_key,
        'data': data
    }
    return data


def reset_index():
    """
    Reset the merging index between different nodes.
    """
    global _memory
    _memory = {}


def get_required_model_param(model, key: str):
    if key not in model:
        raise KeyError(f"Missing required '{key}' in model")
    return model[key]


def _lowercase(string): return str(string).lower()


def _snakecase(string):
    string = re.sub(r"[\-\.\s]", '_', str(string))
    if not string:
        return string
    return _lowercase(string[0]) + re.sub(r"[A-Z]", lambda matched: '_' + _lowercase(matched.group(0)), string[1:])


def _average(value, default=0): return mean(value) if value is not None and isinstance(value, list) else default


def find_term_match(values: list, term_id: str, default_val={}):
    return next((v for v in values if v.get('term', {}).get('@id') == term_id), default_val)


def _non_empty(value): return value != '' and value is not None and value != []


def _non_empty_list(values):
    return list(filter(_non_empty, values)) if isinstance(values, list) else _non_empty(values)


def _filter_by_keys(values, keys: list): return {key: values[key] for key in keys if values.get(key) is not None}


_SKIP_KEYS = ['added', 'addedVersion', 'updated', 'updatedVersion']


def _update_key_version(version: str, node: dict, key: str, is_update=True):
    def update(field: str):
        if key not in _SKIP_KEYS:
            if key in node.get(field, []):
                node.get(f"{field}Version")[node[field].index(key)] = version
            else:
                node[field] = node.get(field, []) + [key]
                node[f"{field}Version"] = node.get(f"{field}Version", []) + [version]
        return node

    return update('updated' if is_update else 'added')


def _safe_deep_update_list_version(version: str, new_data: list, prev_data: list, index: int):
    try:
        new_data[index] = update_node_version(version, new_data[index], prev_data[index])
    except Exception:
        try:
            # try again with an empty value as old data
            new_data[index] = update_node_version(version, new_data[index], {})
        except Exception:
            pass


def _deep_update_node_version(version: str, new_data: Union[dict, list], prev_data: Union[dict, list]):
    if isinstance(new_data, list) and all([isinstance(v, dict) for v in new_data]):
        for index, v in enumerate(new_data):
            _safe_deep_update_list_version(version, new_data, prev_data, index)
    if isinstance(new_data, dict):
        new_data = update_node_version(version, new_data, prev_data)


def update_node_version(version: str, new_data: dict, prev_data: dict = {}):
    """
    Update the node `added` and `updated` fields by comparing the previous fields with the new ones.
    The version of the model adding/updating the fields will be used by default.

    Parameters
    ----------
    version : str
        The version to use in the `addedVersion` or `updatedVersion` field.
    new_data : dict
        The new data.
    prev_data : dict
        Optional - the previous data. If not set, a default empty dictionary will be used as previous value,
        so every field will be marked as "added".

    Returns
    -------
    dict
        The new data with additional `added`, `addedVersion`, `updated` and `updatedVersion` fields.
    """
    def update(prev, key):
        # TODO: do a better comparison
        is_updated = key in prev_data and prev_data.get(key) != new_data.get(key)
        is_added = key not in prev_data
        value = _update_key_version(version, prev, key, is_updated) if is_updated or is_added else prev
        _deep_update_node_version(version, new_data.get(key), prev_data.get(key))
        return value

    keys = [key for key in new_data.keys() if key not in EXCLUDED_VERSION_KEYS]
    return new_data if any([
        prev_data is None,
        # do not add fields on Term
        (prev_data or {}).get('@type') == 'Term',
        new_data.get('@type') == 'Term'
    ]) else reduce(update, keys, new_data)


def new_practice(term: dict): return {'@type': 'Practice', 'term': term}
