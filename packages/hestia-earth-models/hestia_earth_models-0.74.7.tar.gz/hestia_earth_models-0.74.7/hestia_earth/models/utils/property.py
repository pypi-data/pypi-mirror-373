from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.lookup import download_lookup, extract_grouped_data, get_table_value, column_name
from hestia_earth.utils.model import find_term_match, linked_node
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugMissingLookup
from .method import include_methodModel
from .term import download_term, get_lookup_value


def _new_property(term, model=None):
    node = {'@type': SchemaType.PROPERTY.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_term(term, TermTermType.PROPERTY))
    return include_methodModel(node, model)


def merge_properties(properties: list, new_properties: list):
    return properties + [
        p for p in new_properties if not find_term_match(properties, p.get('term', {}).get('@id'))
    ]


def get_property_lookup_value(model: str, term_id: str, column: str):
    term = {'@id': term_id, 'termType': TermTermType.PROPERTY.value}
    return get_lookup_value(term, column, model=model, term=term_id)


def find_term_property(term, property: str, default=None) -> dict:
    """
    Get the property by `@id` linked to the `Term` in the glossary.

    Parameters
    ----------
    term
        The `Term` either as a `str` (`@id` field) or as a `dict` (containing `@id` as a key).
    property : str
        The `term.@id` of the property. Example: `nitrogenContent`.
    default : Any
        The default value if the property is not found. Defaults to `None`.

    Returns
    -------
    dict
        The property if found, `default` otherwise.
    """
    props = term.get('defaultProperties', []) if isinstance(term, dict) else []
    props = (
        download_term(term, TermTermType.PROPERTY) or {}
    ).get('defaultProperties', []) if len(props) == 0 and term else props
    return find_term_match(props, property, default)


def get_node_property(
    node: dict,
    property: str,
    find_default_property: bool = True,
    download_from_hestia: bool = False
) -> dict:
    """
    Get the property by `@id` linked to the Blank Node in the glossary.

    It will search for the `Property` in the following order:
    1. Search in the `properties` of the Blank Node if any was provided
    2. Search in the `defaultProperties` of the `term` by default.

    Parameters
    ----------
    node : dict
        The Blank Node, e.g. an `Input`, `Product`, `Measurement`, etc.
    property : str
        The `term.@id` of the property. Example: `nitrogenContent`.
    find_default_property : bool
        Default to fetching the property from the `defaultProperties` of the `Term`.
    download_from_hestia : bool
        Default to downloading the Term from HESTIA.

    Returns
    -------
    dict
        The property if found, `{}` otherwise.
    """
    return (
        (
            find_term_match(node.get('properties', []), property, None)
        ) or (
            find_term_property(node.get('term', {}), property, None) if find_default_property else None
        ) or (
            {'term': download_term(property, TermTermType.PROPERTY)} if download_from_hestia else None
        ) or {}
    )


def node_has_no_property(term_id: str):
    return lambda product: find_term_match(product.get('properties', []), term_id, None) is None


def node_has_property(term_id: str):
    return lambda product: find_term_match(product.get('properties', []), term_id, None) is not None


def node_property_lookup_value(model: str, node_term: dict, prop_id: str, default=None, **log_args):
    # as the lookup table might not exist, we are making sure we return `0` in thise case
    try:
        lookup_name = f"{node_term.get('termType')}-property.csv"
        term_id = node_term.get('@id')
        lookup_value = get_table_value(download_lookup(lookup_name), 'termid', term_id, column_name(prop_id))
        value = extract_grouped_data(lookup_value, 'Avg') if (
            isinstance(lookup_value, str) and 'Avg' in lookup_value
        ) else lookup_value
        debugMissingLookup(lookup_name, 'termid', term_id, prop_id, value, model=model, **log_args)
        return safe_parse_float(value, default=None)
    except Exception:
        return default


def get_node_property_value(model: str, node: dict, prop_id: str, default=None, handle_percents=True, **log_args):
    prop = get_node_property(node, prop_id, download_from_hestia=True)
    term = prop.get('term')
    units = (term or {}).get('units')
    value = (
        prop['value'] if 'value' in prop else
        node_property_lookup_value(model, node.get('term', {}), prop_id, **log_args)
    )
    return default if value is None else (value / 100 if units == '%' and handle_percents else value)


def get_node_property_value_converted(model: str, node: dict, prop_id: str, default=None, **log_args):
    node_value = list_sum(node.get('value', []))
    prop_value = get_node_property_value(model, node, prop_id, **log_args)
    return default if prop_value is None else node_value * prop_value


def _get_nitrogen_content(node: dict):
    return safe_parse_float(
        get_node_property(node, 'nitrogenContent').get('value', 0), default=0
    ) if node else 0


def _get_nitrogen_tan_content(node: dict):
    return safe_parse_float(
        get_node_property(node, 'totalAmmoniacalNitrogenContentAsN').get('value', 0), default=0
    ) if node else 0
