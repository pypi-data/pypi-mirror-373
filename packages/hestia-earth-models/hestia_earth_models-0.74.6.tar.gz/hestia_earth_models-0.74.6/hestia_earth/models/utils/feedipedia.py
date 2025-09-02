from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, lookup_term_ids
from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import logShouldRun
from .property import _new_property
from .blank_node import merge_blank_nodes

DRY_MATTER_TERM_ID = 'dryMatter'


def get_feedipedia_properties():
    lookup = download_lookup('property.csv')
    term_ids = [
        term_id for term_id in lookup_term_ids(lookup)
        if get_table_value(lookup, 'termid', term_id, column_name('feedipediaName'))
    ]
    return term_ids


def _should_rescale_by_dm(property_id: str):
    lookup = download_lookup('property.csv')
    value = get_table_value(lookup, 'termid', property_id, column_name('feedipediaConversionEnum'))
    return 'dm' in value


def _dm_property(term_id: str, property_values: dict, dm_property_values: dict, dry_matter_property: dict):
    blank_node_data = {}
    for property_key in property_values.keys():
        new_dm_value = safe_parse_float(dry_matter_property.get(property_key), default=None)
        old_dm_value = safe_parse_float(dm_property_values.get(property_key), default=None)
        old_property_value = safe_parse_float(property_values.get(property_key), default=None)
        if all([new_dm_value, old_dm_value, old_property_value]):
            new_value = round(
                old_property_value / old_dm_value * new_dm_value,
                2
            ) if _should_rescale_by_dm(term_id) else old_property_value
            blank_node_data[property_key] = new_value
    return (_new_property(term_id) | blank_node_data) if blank_node_data else None


def _map_properties(lookup, term_id: str, column_prefix: str):
    value = get_table_value(lookup, 'termid', term_id, column_name(column_prefix))
    sd = get_table_value(lookup, 'termid', term_id, column_name(f"{column_prefix}-sd"))
    min = get_table_value(lookup, 'termid', term_id, column_name(f"{column_prefix}-min"))
    max = get_table_value(lookup, 'termid', term_id, column_name(f"{column_prefix}-max"))
    return {'value': value, 'sd': sd, 'min': min, 'max': max}


def rescale_properties_from_dryMatter(model: str, node: dict, blank_nodes: list, **log_args):
    properties = get_feedipedia_properties()
    # download all to save time
    term_types = [blank_node.get('term', {}).get('termType') for blank_node in blank_nodes]
    term_types_lookups = {term_type: download_lookup(f"{term_type}-property.csv") for term_type in term_types}

    def exec_property(blank_node: dict, property_id: str, dry_matter_property: dict):
        term_id = blank_node.get('term', {}).get('@id')
        term_type = blank_node.get('term', {}).get('termType')
        lookup = term_types_lookups[term_type]

        return _dm_property(
            property_id,
            _map_properties(lookup, term_id, column_prefix=property_id),
            _map_properties(lookup, term_id, column_prefix=DRY_MATTER_TERM_ID),
            dry_matter_property
        ) if all([property_id]) else None

    def exec(blank_node: dict):
        term_id = blank_node.get('term', {}).get('@id')
        all_properties = blank_node.get('properties', [])
        dry_matter_property = find_term_match(all_properties, DRY_MATTER_TERM_ID)
        # get all values for this term that have a special property
        new_properties = non_empty_list([
            exec_property(blank_node, p, dry_matter_property) for p in properties if all([
                not find_term_match(all_properties, p),
                p != DRY_MATTER_TERM_ID,
                dry_matter_property
            ])
        ])
        for prop in new_properties:
            logShouldRun(node, model, term_id, True, property=prop.get('term', {}).get('@id'), **log_args)
        return (
            blank_node | {'properties': merge_blank_nodes(all_properties, new_properties)}
        ) if new_properties else blank_node

    return list(map(exec, blank_nodes))
