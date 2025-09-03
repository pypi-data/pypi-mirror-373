from statistics import mean
from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data
from hestia_earth.utils.model import find_primary_product, filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugMissingLookup


def get_default_digestibility(model: str, term_id: str, cycle: dict):
    """
    Return default Digestibility for a Live Animal in a specific System.

    Parameters
    ----------
    cycle : dict
        A `Cycle`. The `primary` Product must be a `liveAnimal` and the practices must contain a `system`.

    Returns
    -------
    float
        The default digestibility. Returns `None` if no matching value.
    """
    product = find_primary_product(cycle) or {}
    product_id = product.get('term', {}).get('@id')
    is_liveAnimal = product.get('term', {}).get('termType') == TermTermType.LIVEANIMAL.value
    systems = filter_list_term_type(cycle.get('practices', []), TermTermType.SYSTEM) if is_liveAnimal else []
    lookup_name = 'system-liveAnimal-digestibility-2019.csv'
    lookup = download_lookup(lookup_name) if is_liveAnimal else None

    for system in systems:
        system_id = system.get('term', {}).get('@id')
        lookup_col = column_name(product_id)
        value = get_table_value(lookup, 'termid', system_id, lookup_col)
        debugMissingLookup(lookup_name, 'termid', term_id, lookup_col, value, model=model, term=term_id)
        min = safe_parse_float(extract_grouped_data(value, 'min'), default=None)
        max = safe_parse_float(extract_grouped_data(value, 'max'), default=None)
        if min and max:
            return mean([min, max])

    return None
