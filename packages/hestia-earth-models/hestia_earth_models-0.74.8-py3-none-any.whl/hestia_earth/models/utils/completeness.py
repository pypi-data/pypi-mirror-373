from typing import Union
from hestia_earth.schema import Completeness, TermTermType

from .term import download_term

completeness_fields = Completeness().required


def _completeness_term_type(cycle: dict, term: Union[str, dict, TermTermType]):
    return (
        term if term in cycle.get('completeness', {}) or term in completeness_fields else None
    ) if isinstance(term, str) else None if isinstance(term, dict) else term.value


def _get_term_type_completeness(cycle: dict, term: Union[str, dict]):
    term = download_term(term) if isinstance(term, str) else term
    term_type = term.get('termType') if term else None
    return cycle.get('completeness', {}).get(term_type, False)


def _completeness_value(cycle: dict, term: Union[str, dict, TermTermType]):
    term_type = _completeness_term_type(cycle, term)
    return _get_term_type_completeness(cycle, term) if term_type is None else (
        cycle.get('completeness', {}).get(term_type, False)
    )


def _is_term_type_complete(cycle: dict, term: Union[str, dict, TermTermType]):
    return _completeness_value(cycle, term) is True


def _is_term_type_incomplete(cycle: dict, term: Union[str, dict, TermTermType]):
    return _completeness_value(cycle, term) is False
