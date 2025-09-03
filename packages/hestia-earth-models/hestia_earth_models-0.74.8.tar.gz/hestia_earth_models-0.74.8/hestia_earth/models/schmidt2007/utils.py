from hestia_earth.schema import NodeType, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.lookup import all_factor_value
from . import MODEL


def get_waste_values(term_id: str, cycle: dict, lookup_col: str):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.WASTE)
    value = all_factor_value(
        log_model=MODEL,
        log_term_id=term_id,
        log_node=cycle,
        lookup_name=f"{TermTermType.WASTE.value}.csv",
        lookup_col=lookup_col,
        blank_nodes=products,
        default_no_values=None
    )
    return [0] if all([
        value is None,
        _is_term_type_complete(cycle, TermTermType.WASTE),
        cycle.get('@type', cycle.get('type')) == NodeType.CYCLE.value  # ignore adding 0 value for Transformation
    ]) else non_empty_list([value])
