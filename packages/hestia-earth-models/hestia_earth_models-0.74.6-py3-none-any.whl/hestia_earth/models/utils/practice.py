from hestia_earth.schema import SchemaType
from hestia_earth.utils.model import linked_node

from .term import download_term
from .method import include_model


def _new_practice(term, model=None):
    node = {'@type': SchemaType.PRACTICE.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_term(term))
    return include_model(node, model)
