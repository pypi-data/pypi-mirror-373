from hestia_earth.schema import TermTermType

from .term import get_lookup_value


def get_pef_grouping(term_id: str):
    term = {'@id': term_id, 'termType': TermTermType.LANDCOVER.value}
    grouping = get_lookup_value(term, column='pefTermGrouping')
    return f"{grouping}" if grouping else None
