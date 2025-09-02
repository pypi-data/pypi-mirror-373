import pydash
from datetime import datetime
from hestia_earth.schema import UNIQUENESS_FIELDS
from hestia_earth.utils.tools import safe_parse_date, flatten

from hestia_earth.orchestrator.utils import (
    _non_empty_list,
    update_node_version,
    wrap_index,
    update_index
)
from .merge_node import merge as merge_node

_METHOD_MODEL_KEY = 'methodModel.@id'


def _matching_properties(model: dict, node_type: str):
    return UNIQUENESS_FIELDS.get(node_type, {}).get(model.get('key'), [])


def _has_property(value: dict, key: str):
    keys = key.split('.')
    is_list = len(keys) >= 2 and isinstance(pydash.objects.get(value, keys[0]), list)
    values = [
        pydash.objects.get(v, '.'.join(keys[1:])) for v in pydash.objects.get(value, keys[0])
    ] if is_list else [
        pydash.objects.get(value, key)
    ]
    return all([v is not None for v in values])


def _values_have_property(values: list, key: str): return any([_has_property(v, key) for v in values])


def _handle_local_property(values: list, properties: list, local_id: str):
    # Handle "impactAssessment.@id" if present in the data
    existing_id = local_id.replace('.id', '.@id')

    if local_id in properties:
        # remove if not used
        if not _values_have_property(values, local_id):
            properties.remove(local_id)

        # add if used
        if _values_have_property(values, existing_id):
            properties.append(existing_id)

    return properties


def _get_value(data: dict, key: str, merge_args: dict = {}):
    value = pydash.objects.get(data, key)
    date = safe_parse_date(value) if key in ['startDate', 'endDate'] else None
    return datetime.strftime(date, merge_args.get('matchDatesFormat', '%Y-%m-%d')) if date else value


def _value_index_key(value: dict, properties: list, merge_args: dict = {}):
    def property_value(key: str):
        keys = key.split('.')
        prop_value = _get_value(value, key, merge_args)
        is_list = len(keys) >= 2 and isinstance(pydash.objects.get(value, keys[0]), list)
        return sorted(_non_empty_list([
            pydash.objects.get(x, '.'.join(keys[1:]))
            for x in pydash.objects.get(value, keys[0], [])
        ])) if is_list else prop_value

    source_properties = [p for p in properties if _has_property(value, p)]
    return '-'.join(map(str, flatten(map(property_value, source_properties))))


def _build_matching_properties(values: list, model: dict = {}, merge_args: dict = {}, node_type: str = ''):
    # only merge node if it has the same `methodModel`
    same_methodModel = merge_args.get('sameMethodModel', False)

    properties = _matching_properties(model, node_type)
    properties = list(set(properties + [_METHOD_MODEL_KEY])) if same_methodModel else [
        p for p in properties if p != _METHOD_MODEL_KEY
    ]
    return _handle_local_property(values, properties, 'impactAssessment.id')


def merge(
    source: list,
    new_values: list,
    version: str,
    model: dict = {},
    merge_args: dict = {},
    node_type: str = ''
):
    source = [] if source is None else source

    # only merge if the
    skip_same_term = merge_args.get('skipSameTerm', False)

    # build list of properties used to do the matching
    properties = _build_matching_properties(source, model, merge_args, node_type)

    # store previous identical index to speed merging
    index_key = '-'.join([node_type, model.get('key', '')])
    # when the subkey changes, we need to completely rebuild the index
    index_sub_key = '-'.join(properties + [str(merge_args)])

    def build_index():
        return {
            _value_index_key(value, properties, merge_args): index
            for index, value in enumerate(source)
        } if properties else None

    source_index_keys = wrap_index(index_key, index_sub_key, build_index)

    for el in _non_empty_list(new_values):
        new_value_index_key = _value_index_key(el, properties, merge_args)
        source_index = source_index_keys.get(new_value_index_key) if source_index_keys else None
        if source_index is None:
            # add to index keys for next elements
            source_index_keys = source_index_keys or {}
            source_index_keys[new_value_index_key] = len(source)
            source.append(update_node_version(version, el))
        elif not skip_same_term:
            source[source_index] = merge_node(source[source_index], el, version, model, merge_args)

    update_index(index_key, index_sub_key, source_index_keys)

    return source
