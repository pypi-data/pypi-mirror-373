from typing import Union
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import linked_node

from .term import download_term


def include_method(node: dict, term_id: Union[None, str, dict], key='method'):
    term = (
        download_term(term_id, TermTermType.MODEL) or download_term(term_id) or {}
    ) if isinstance(term_id, str) else term_id
    return node | ({} if term is None or term.get('@id') is None else {key: linked_node(term)})


def include_model(node: dict, term_id: Union[None, str, dict]):
    return include_method(node, term_id=term_id, key='model')


def include_methodModel(node: dict, term_id: Union[None, str, dict]):
    return include_method(node, term_id=term_id, key='methodModel')
